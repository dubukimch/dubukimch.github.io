#!/usr/bin/env python3
"""Check public manual pages against reviewed evidence, without HTTP or writes.

Run after sync-manual-content.py and build-current-site.py. This verifies static
content and file identity; it does not claim browser or application execution.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
STATES = Counter(full=37, partial=1, unverified=3)
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def digest(path):
    assert path.is_file(), f"Missing file: {path}"
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_file(root, path):
    result = (root / unquote(path)).resolve()
    assert result.is_relative_to(root), f"Path outside root: {path}"
    assert result.is_file(), f"Missing file: {path}"
    return result


class Document(HTMLParser):
    def __init__(self, path, operation_ids):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = set()
        self.operations = {}
        self.stack = []
        self.h1 = 0
        self.operation_ids = operation_ids
        self.feed(path.read_text(encoding="utf-8-sig"))

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            assert values["id"] not in self.ids, f"Duplicate HTML id: {values['id']}"
            self.ids.add(values["id"])
        self.h1 += tag == "h1"
        current = self.stack[-1][1] if self.stack else None
        identity = values.get("data-operation") or values.get("data-operation-id") or values.get("id", "")
        if identity.startswith("op-") and identity[3:] in self.operation_ids:
            identity = identity[3:]
        if tag in {"section", "article"} and identity in self.operation_ids:
            assert identity not in self.operations, f"Duplicate operation section: {identity}"
            current = identity
            self.operations[current] = {"images": [], "links": [], "text": [], "state": values.get("data-evidence-state") or values.get("data-evidence")}
        for attr in ("href", "src", "data-lightbox"):
            if values.get(attr):
                self.links.append(values[attr])
                if current:
                    self.operations[current]["links"].append(values[attr])
        if tag == "img" and current and values.get("src"):
            self.operations[current]["images"].append(values["src"])
        if tag not in VOID_TAGS:
            self.stack.append((tag, current))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_data(self, data):
        current = self.stack[-1][1] if self.stack else None
        if current:
            self.operations[current]["text"].append(data)


def markdown_targets(text):
    return re.findall(r"!?\[[^\]]*\]\(([^\)]+)\)", text)


def markdown_prose(text):
    return re.sub(r"(!?\[[^\]]*\]\()([^\)]+)(\))", r"\1LINK\3", text).replace("\r\n", "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT.parent / "솔루션_사용매뉴얼/2026-10-24")
    parser.add_argument("--mirror", type=Path, default=ROOT.parent / "포트폴리오")
    args = parser.parse_args()
    source, mirror = args.source.resolve(), args.mirror.resolve()
    manual = read_json(ROOT / "content/manuals.json")
    asset_manifest = read_json(ROOT / "content/manual-assets.json")
    reviewed = read_json(source / "data/manual-manifest.json")
    visual = read_json(source / "data/visual-copy.json")
    products = manual["products"]
    operations = [operation for product in products for operation in product["operations"]]
    operation_ids = {operation["id"] for operation in operations}
    assert len(products) == len({p["id"] for p in products}) == 7, "Seven unique products required"
    assert len(operations) == len(operation_ids) == 41, "41 unique operations required"
    assert Counter(o["evidenceState"] for o in operations) == STATES, "Evidence states changed"
    assert len({o["screenshot"] for o in operations if o["screenshot"]}) == 38, "38 captures required"
    assert manual["stats"] | {"icons": None} == {"products": 7, "operations": 41, "screenshots": 38, "pdfPages": 56, "full": 37, "partial": 1, "unverified": 3, "icons": None}, "Incorrect public counts"
    assert asset_manifest["sourceManifestSha256"] == digest(source / "data/manual-manifest.json"), "Stale source manifest"

    slides = {s["operation"]: s for s in reviewed["slides"] if s.get("kind") == "operation"}
    chapters = {s["chapter"]: s["number"] for s in reviewed["slides"] if s.get("kind") == "chapter"}
    assert set(slides) == operation_ids, "Reviewed operation coverage differs"
    pdf_path = local_file(ROOT, manual["downloads"]["pdf"])
    pdf_pages = len(PdfReader(pdf_path).pages)
    assert pdf_pages == len(reviewed["slides"]) == 56, "PDF page count differs"
    assert digest(pdf_path) == digest(source / "산업솔루션_통합사용매뉴얼.pdf"), "PDF source differs"
    pptx_path = local_file(ROOT, manual["downloads"]["pptx"])
    assert digest(pptx_path) == digest(source / "산업솔루션_통합사용매뉴얼.pptx"), "PPTX source differs"
    with ZipFile(pptx_path) as deck:
        assert len([n for n in deck.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]) == pdf_pages, "PPTX/PDF pagination differs"

    documents = {p.name: Document(p, operation_ids) for p in ROOT.glob("*.html")}
    assert len(documents) == 18, "Expected 18 portfolio and manual HTML pages"
    manual_pages = {p["manualPage"] for p in products}
    assert len(manual_pages) == 7 and manual_pages <= documents.keys(), "Seven manual guides missing"
    assert "manuals.html" in documents and manual_pages <= set(documents["manuals.html"].links), "Manual hub must link to all seven guides"
    mirrored = {"content/manuals.json", "content/manual-assets.json", manual["iconLicense"], manual["iconSources"], "assets/icons/lucide/icon-provenance.json", *manual["downloads"].values()}
    local_links = set()
    for name, document in documents.items():
        assert document.h1 == 1, f"Expected one h1: {name}"
        mirrored.add(name)
        for url in document.links:
            parts = urlsplit(url)
            if parts.scheme or parts.netloc:
                continue
            target = local_file(ROOT, parts.path or name)
            relative = target.relative_to(ROOT).as_posix()
            local_links.add(relative)
            mirrored.add(relative)
            if parts.fragment and target.suffix == ".html":
                assert unquote(parts.fragment) in documents[target.name].ids, f"Broken HTML fragment: {name}: {url}"
            elif parts.fragment and target.suffix == ".pdf":
                assert re.fullmatch(r"page=[1-9]\d*", parts.fragment), f"Invalid PDF page fragment: {url}"
                assert int(parts.fragment[5:]) <= pdf_pages, f"PDF page outside document: {url}"

    md_links = 0
    seen_captures = set()
    for product in products:
        detail = documents[product["portfolioPage"]]
        guide = documents[product["manualPage"]]
        chapter = read_json(source / "data" / (product["sourceId"] + ".json"))
        originals = {o["id"]: o for o in chapter["operations"]}
        assert {o["id"] for o in product["operations"]} == set(originals), f"Public chapter coverage differs: {product['id']}"
        assert set(guide.operations) == set(originals), f"Missing operation sections: {product['id']}"
        assert product["chapterPdfPage"] == product["pdfPageStart"] == chapters[product["manifestChapterId"]], "Chapter PDF page differs"
        assert product["pdfPageEnd"] == product["operations"][-1]["pdfPage"], "Chapter ending page differs"
        assert product["pdfUrl"] == f"{manual['downloads']['pdf']}#page={product['chapterPdfPage']}", "Chapter PDF URL differs"
        for url in (product["manualPage"], product["pdfUrl"], product["markdown"]):
            assert url in detail.links, f"Solution detail lacks manual attachment: {product['id']}: {url}"
        assert product["pdfUrl"] in guide.links and product["markdown"] in guide.links, f"Guide downloads missing: {product['id']}"
        state_counts = Counter(o["evidenceState"] for o in product["operations"])
        assert product["counts"] == {"operations": len(originals), "screenshots": sum(bool(o["screenshot"]) for o in product["operations"]), **{state: state_counts[state] for state in STATES}}, "Chapter evidence counts differ"
        markdown = local_file(ROOT, product["markdown"])
        md_text = markdown.read_text(encoding="utf-8-sig")
        assert markdown_prose(md_text) == markdown_prose((source / "chapters" / (product["sourceId"] + ".md")).read_text(encoding="utf-8-sig")), "Markdown prose differs from reviewed source"
        mirrored.add(product["markdown"])
        for target in markdown_targets(md_text):
            parts = urlsplit(target)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            resolved = (markdown.parent / unquote(parts.path)).resolve()
            assert resolved.is_relative_to(ROOT) and resolved.is_file(), f"Broken Markdown link: {product['markdown']}: {target}"
            mirrored.add(resolved.relative_to(ROOT).as_posix())
            md_links += 1
        for operation in product["operations"]:
            identity = operation["id"]
            original, rendered, slide = originals[identity], guide.operations[identity], slides[identity]
            for field in ("title", "goal", "steps", "expected", "troubleshooting", "verified", "evidence"):
                assert operation[field] == original.get(field), f"Reviewed detail changed: {identity}.{field}"
            assert operation["evidenceState"] == visual["operations"][identity]["evidenceState"], f"Evidence changed: {identity}"
            assert operation["pdfPage"] == slide["number"], f"Operation PDF page differs: {identity}"
            assert operation["pdfUrl"] == f"{manual['downloads']['pdf']}#page={slide['number']}", f"Operation PDF URL differs: {identity}"
            assert operation["pdfUrl"] in rendered["links"], f"Operation PDF link missing: {identity}"
            assert rendered["state"] == operation["evidenceState"], f"HTML evidence state differs: {identity}"
            if operation["screenshot"]:
                capture = local_file(ROOT, operation["screenshot"])
                assert operation["screenshot"] in rendered["images"], f"Capture missing from operation: {identity}"
                assert digest(capture) == original["evidence"]["sha256"] == digest(source / original["screenshot"]), f"Capture bytes changed: {identity}"
                seen_captures.add(operation["screenshot"])
            else:
                assert operation["evidenceState"] == "unverified" and product["id"] == "oee", f"Unexpected uncaptured procedure: {identity}"
                assert not original.get("screenshot") and not operation["evidence"], f"Unverified procedure has capture evidence: {identity}"
                assert not [url for url in rendered["images"] if urlsplit(url).path.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))], f"Unverified procedure has a fabricated capture: {identity}"
                assert any(label in "".join(rendered["text"]) for label in ("미검증", "실행 미확인")), f"Unverified label missing: {identity}"
    assert len(seen_captures) == 38, "Rendered capture coverage differs"

    for record in asset_manifest["files"]:
        assert digest(local_file(ROOT, record["path"])) == record["sha256"] == digest(local_file(source, record["source"])), f"Public source identity differs: {record['path']}"
        mirrored.add(record["path"])
    icon_provenance = read_json(ROOT / "assets/icons/lucide/icon-provenance.json")
    assert len(icon_provenance["assets"]) == manual["stats"]["icons"], "Icon provenance count differs"
    assert digest(local_file(ROOT, manual["iconLicense"])) == digest(source / "assets/design/LICENSE-Lucide.txt"), "Official icon license changed"
    for icon in icon_provenance["assets"]:
        assert digest(local_file(ROOT, icon["path"])) == icon["sha256"], f"Official icon changed: {icon['path']}"
    for relative in sorted(mirrored):
        assert digest(local_file(ROOT, relative)) == digest(local_file(mirror, relative)), f"Stale portfolio mirror: {relative}"
    print(json.dumps({"status": "PASS", "html_pages": len(documents), "manual_guides": len(products), "operations": len(operations), "screenshots": len(seen_captures), "evidence_states": dict(STATES), "pdf_pages": pdf_pages, "markdown_local_links": md_links, "official_icons": manual["stats"]["icons"], "local_resources": len(local_links), "mirror_files": len(mirrored), "external_requests": 0, "scope": "Static source, links, pagination, evidence and mirror identity; no browser or solution execution claimed"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
