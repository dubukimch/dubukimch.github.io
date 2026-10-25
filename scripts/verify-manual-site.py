#!/usr/bin/env python3
"""Check public manual pages against reviewed evidence, without HTTP or writes.

Run after sync-manual-content.py and build-current-site.py. This verifies static
content and file identity; it does not claim browser or application execution.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import io
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from pypdf import PdfReader
from PIL import Image


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
        self.text = []
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
        self.text.append(data)
        current = self.stack[-1][1] if self.stack else None
        if current:
            self.operations[current]["text"].append(data)


def markdown_targets(text):
    return re.findall(r"!?\[[^\]]*\]\(([^\)]+)\)", text)


def markdown_prose(text):
    return re.sub(r"(!?\[[^\]]*\]\()([^\)]+)(\))", r"\1LINK\3", text).replace("\r\n", "\n")


def without_current_step_sections(text, operations):
    sections = re.split(r"(?=^## \d+\.)", text, flags=re.M)
    changed_titles = {operation["title"] for operation in operations if operation.get("originalSteps")}
    return "".join(section for section in sections if not any(re.search(r"^## \d+\. " + re.escape(title) + r"\s*$", section, flags=re.M) for title in changed_titles))


def verify_publication(publication):
    page_limits = {}
    media_count = 0
    entries = [publication["integrated"], *publication["solutions"]]
    assert len(entries) == 8 and len({item["id"] for item in publication["solutions"]}) == 7
    for entry in entries:
        if entry is not publication["integrated"]:
            assert entry["slides"] == len(entry["operationPages"]) + 3
            assert sorted(entry["operationPages"].values()) == list(range(3, entry["slides"])), "Standalone operation order differs"
        for extension in ("pdf", "pptx"):
            artifact = entry[extension]
            file = local_file(ROOT, artifact["path"])
            assert file.stat().st_size == artifact["bytes"] and digest(file) == artifact["sha256"], f"Artifact identity differs: {artifact['path']}"
        pdf = local_file(ROOT, entry["pdf"]["path"])
        assert len(PdfReader(pdf).pages) == entry["slides"], f"Standalone PDF page count differs: {pdf.name}"
        page_limits[entry["pdf"]["path"]] = entry["slides"]
        with ZipFile(local_file(ROOT, entry["pptx"]["path"])) as deck:
            assert deck.testzip() is None
            slides = [name for name in deck.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)]
            assert len(slides) == entry["slides"], f"Standalone PPTX page count differs: {entry.get('id', 'integrated')}"
            for name in deck.namelist():
                if not name.startswith("ppt/media/"):
                    continue
                assert not name.endswith(".svg"), f"Unrepaired SVG compatibility image: {name}"
                with Image.open(io.BytesIO(deck.read(name))) as image:
                    image.load()
                    assert image.width > 1 and image.height > 1, f"Placeholder fallback image: {name}"
                    media_count += 1
    for extension, alias in publication["legacyDownloads"].items():
        assert digest(local_file(ROOT, alias)) == publication["integrated"][extension]["sha256"], "Legacy public link still serves an old artifact"
    return page_limits, media_count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT.parent / "솔루션_사용매뉴얼/2026-10-24")
    parser.add_argument("--mirror", type=Path, default=ROOT.parent / "포트폴리오")
    parser.add_argument("--publication-manifest", type=Path, default=ROOT.parent / "솔루션_사용매뉴얼/2026-10-25/publication-manifest.json")
    args = parser.parse_args()
    source, mirror = args.source.resolve(), args.mirror.resolve()
    manual = read_json(ROOT / "content/manuals.json")
    asset_manifest = read_json(ROOT / "content/manual-assets.json")
    reviewed = read_json(source / "data/manual-manifest.json")
    visual = read_json(source / "data/visual-copy.json")
    publication = read_json(ROOT / manual["publication"]) if manual.get("publication") else None
    refreshes = {item["id"]: item for item in publication.get("captureRefresh", [])} if publication else {}
    expected_states = Counter(STATES)
    for identity, refresh in refreshes.items():
        expected_states[visual["operations"][identity]["evidenceState"]] -= 1
        expected_states[refresh["evidenceState"]] += 1
    products = manual["products"]
    operations = [operation for product in products for operation in product["operations"]]
    operation_ids = {operation["id"] for operation in operations}
    assert len(products) == len({p["id"] for p in products}) == 7, "Seven unique products required"
    assert len(operations) == len(operation_ids) == 41, "41 unique operations required"
    assert Counter(o["evidenceState"] for o in operations) == expected_states, "Evidence states differ from reviewed capture refresh"
    assert len({o["screenshot"] for o in operations if o["screenshot"]}) == 38, "38 captures required"
    for key, value in {"products": 7, "operations": 41, "screenshots": 38, "pdfPages": 56, **{state: expected_states[state] for state in STATES}}.items():
        assert manual["stats"][key] == value, f"Incorrect public count: {key}"
    assert asset_manifest["sourceManifestSha256"] == digest(source / "data/manual-manifest.json"), "Stale source manifest"

    slides = {s["operation"]: s for s in reviewed["slides"] if s.get("kind") == "operation"}
    chapters = {s["chapter"]: s["number"] for s in reviewed["slides"] if s.get("kind") == "chapter"}
    assert set(slides) == operation_ids, "Reviewed operation coverage differs"
    pdf_path = local_file(ROOT, manual["downloads"]["pdf"])
    integrated_reader = PdfReader(pdf_path)
    pdf_pages = len(integrated_reader.pages)
    assert pdf_pages == len(reviewed["slides"]) == 56, "PDF page count differs"
    pptx_path = local_file(ROOT, manual["downloads"]["pptx"])
    if not publication:
        assert digest(pdf_path) == digest(source / "산업솔루션_통합사용매뉴얼.pdf"), "PDF source differs"
        assert digest(pptx_path) == digest(source / "산업솔루션_통합사용매뉴얼.pptx"), "PPTX source differs"
    page_limits, checked_media = verify_publication(publication) if publication else ({manual['downloads']['pdf']: pdf_pages}, 0)
    if publication and args.publication_manifest.is_file():
        assert publication["sourceManifestSha256"] == digest(args.publication_manifest), "Publication source manifest differs"
    dedicated_documents = {item["id"]: item for item in publication["solutions"]} if publication else {}
    if publication:
        assert publication["integrated"]["operationPages"] == {identity: slide["number"] for identity, slide in slides.items()}, "Integrated publication operation pages differ"
    with ZipFile(pptx_path) as deck:
        assert len([n for n in deck.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)]) == pdf_pages, "PPTX/PDF pagination differs"

    documents = {p.name: Document(p, operation_ids) for p in ROOT.glob("*.html")}
    assert len(documents) == 18, "Expected 18 portfolio and manual HTML pages"
    manual_pages = {p["manualPage"] for p in products}
    assert len(manual_pages) == 7 and manual_pages <= documents.keys(), "Seven manual guides missing"
    assert "manuals.html" in documents and manual_pages <= set(documents["manuals.html"].links), "Manual hub must link to all seven guides"
    mirrored = {"content/manuals.json", "content/manual-assets.json", manual["iconLicense"], manual["iconSources"], "assets/icons/lucide/icon-provenance.json", *manual["downloads"].values()}
    if publication:
        mirrored.add(manual["publication"])
        mirrored.update(publication["legacyDownloads"].values())
        for entry in [publication["integrated"], *publication["solutions"]]:
            mirrored.update(entry[extension]["path"] for extension in ("pdf", "pptx"))
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
                limit = page_limits.get(relative)
                assert limit and int(parts.fragment[5:]) <= limit, f"PDF page outside document: {url}"

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
        if product["id"] in dedicated_documents:
            dedicated = dedicated_documents[product["id"]]
            dedicated_reader = PdfReader(local_file(ROOT, dedicated["pdf"]["path"]))
            assert product["standalonePages"] == dedicated["slides"]
            for extension in ("pdf", "pptx"):
                url = dedicated[extension]["path"]
                assert product["downloads"][extension] == url
                assert all(url in documents[name].links for name in (product["portfolioPage"], product["manualPage"], "manuals.html")), f"Dedicated {extension} attachment missing: {product['id']}"
        state_counts = Counter(o["evidenceState"] for o in product["operations"])
        assert product["counts"] == {"operations": len(originals), "screenshots": sum(bool(o["screenshot"]) for o in product["operations"]), **{state: state_counts[state] for state in STATES}}, "Chapter evidence counts differ"
        markdown = local_file(ROOT, product["markdown"])
        md_text = markdown.read_text(encoding="utf-8-sig")
        source_md = (source / "chapters" / (product["sourceId"] + ".md")).read_text(encoding="utf-8-sig")
        if product.get("originalPrerequisites"):
            assert product["originalPrerequisites"] == chapter["prerequisites"]
            assert product["prerequisites"] == publication["productOverrides"][product["id"]]["prerequisites"]
            for before, after in zip(product["originalPrerequisites"], product["prerequisites"]):
                source_md = source_md.replace("- " + before, "- " + after, 1)
                assert after in md_text and after in "".join(guide.text), "Current prerequisites missing from Markdown or HTML"
        if any(operation["id"] in refreshes for operation in product["operations"]):
            source_md_core = without_current_step_sections(source_md, product["operations"])
            md_comparison = without_current_step_sections(md_text, product["operations"])
            md_text_core = re.sub(r"^(관측 결과|캡처 안내|검증 범위):.*$", "", md_comparison, flags=re.M)
            source_md = re.sub(r"^(관측 결과|캡처 안내|검증 범위):.*$", "", source_md_core, flags=re.M)
        else:
            md_text_core = md_text
        assert markdown_prose(md_text_core) == markdown_prose(source_md), "Markdown procedure prose differs from reviewed source"
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
            for field in ("title", "goal", "troubleshooting", "verified"):
                assert operation[field] == original.get(field), f"Reviewed detail changed: {identity}.{field}"
            if operation.get("originalSteps"):
                assert operation["originalSteps"] == original["steps"] and operation["originalExpected"] == original["expected"]
                assert operation["steps"] == refreshes[identity]["currentSteps"] and operation["expected"] == refreshes[identity]["currentExpected"]
                assert operation["stages"] == refreshes[identity]["stages"]
                for step in operation["steps"]:
                    assert step in md_text and step in "".join(rendered["text"]), f"Current procedure missing from Markdown or HTML: {identity}"
                for field in ("title", "goal", "expected"):
                    assert operation[field] in md_text, f"Current Markdown content missing: {identity}.{field}"
                assert operation["legacyEvidenceNote"] in md_text, f"Historical evidence distinction missing: {identity}"
            else:
                assert operation["steps"] == original["steps"] and operation["expected"] == original["expected"]
            if identity in refreshes:
                assert operation["originalEvidence"] == original["evidence"]
                assert operation["evidence"] == refreshes[identity]["evidence"]
                assert operation["evidenceState"] == refreshes[identity]["evidenceState"]
            else:
                assert operation["evidence"] == original.get("evidence")
                assert operation["evidenceState"] == visual["operations"][identity]["evidenceState"], f"Evidence changed: {identity}"
            assert operation["pdfPage"] == slide["number"], f"Operation PDF page differs: {identity}"
            assert operation["pdfUrl"] == f"{manual['downloads']['pdf']}#page={slide['number']}", f"Operation PDF URL differs: {identity}"
            assert operation["pdfUrl"] in rendered["links"], f"Operation PDF link missing: {identity}"
            title = re.sub(r"\s+", "", operation["shortTitle"])
            assert title in re.sub(r"\s+", "", integrated_reader.pages[operation["pdfPage"]-1].extract_text()), f"Integrated PDF title differs at linked page: {identity}"
            if product["id"] in dedicated_documents:
                local_page = dedicated_documents[product["id"]]["operationPages"][identity]
                assert operation["standalonePdfPage"] == local_page
                assert operation["standalonePdfUrl"] == f"{product['downloads']['pdf']}#page={local_page}"
                assert operation["standalonePdfUrl"] in rendered["links"], f"Dedicated operation PDF link missing: {identity}"
                assert title in re.sub(r"\s+", "", dedicated_reader.pages[local_page-1].extract_text()), f"Dedicated PDF title differs at linked page: {identity}"
            assert rendered["state"] == operation["evidenceState"], f"HTML evidence state differs: {identity}"
            if operation["screenshot"]:
                capture = local_file(ROOT, operation["screenshot"])
                assert operation["screenshot"] in rendered["images"], f"Capture missing from operation: {identity}"
                assert digest(source / original["screenshot"]) == original["evidence"]["sha256"], f"Frozen source capture changed: {identity}"
                assert digest(capture) == operation["evidence"]["sha256"], f"Current capture bytes changed: {identity}"
                seen_captures.add(operation["screenshot"])
            else:
                assert operation["evidenceState"] == "unverified" and product["id"] == "oee", f"Unexpected uncaptured procedure: {identity}"
                assert not original.get("screenshot") and not operation["evidence"], f"Unverified procedure has capture evidence: {identity}"
                assert not [url for url in rendered["images"] if urlsplit(url).path.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))], f"Unverified procedure has a fabricated capture: {identity}"
                assert any(label in "".join(rendered["text"]) for label in ("미검증", "실행 미확인")), f"Unverified label missing: {identity}"
    assert len(seen_captures) == 38, "Rendered capture coverage differs"

    for record in asset_manifest["files"]:
        origin_root = source.parent / record.get("sourceEdition", source.name)
        assert digest(local_file(ROOT, record["path"])) == record["sha256"] == digest(local_file(origin_root, record["source"])), f"Public source identity differs: {record['path']}"
        mirrored.add(record["path"])
    icon_provenance = read_json(ROOT / "assets/icons/lucide/icon-provenance.json")
    assert len(icon_provenance["assets"]) == manual["stats"]["icons"], "Icon provenance count differs"
    assert digest(local_file(ROOT, manual["iconLicense"])) == digest(source / "assets/design/LICENSE-Lucide.txt"), "Official icon license changed"
    for icon in icon_provenance["assets"]:
        assert digest(local_file(ROOT, icon["path"])) == icon["sha256"], f"Official icon changed: {icon['path']}"
    for relative in sorted(mirrored):
        assert digest(local_file(ROOT, relative)) == digest(local_file(mirror, relative)), f"Stale portfolio mirror: {relative}"
    print(json.dumps({"status": "PASS", "html_pages": len(documents), "manual_guides": len(products), "operations": len(operations), "screenshots": len(seen_captures), "evidence_states": {state: expected_states[state] for state in STATES}, "publication_files": 16 if publication else 2, "pptx_media_images_decoded": checked_media, "pdf_pages": pdf_pages, "markdown_local_links": md_links, "official_icons": manual["stats"]["icons"], "local_resources": len(local_links), "mirror_files": len(mirrored), "external_requests": 0, "scope": "Static source, links, pagination, evidence and mirror identity; no browser or solution execution claimed"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
