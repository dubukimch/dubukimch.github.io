#!/usr/bin/env python3
"""Publish the reviewed manual's public content without changing its evidence.

The reviewed manual folder is the only source. This script uses the Python
standard library, copies screenshots byte for byte, rewrites Markdown links,
and derives PDF page numbers from the final presentation manifest.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import re
import shutil


ROOT = Path(__file__).resolve().parents[1]
EDITION = "2026-10-24"
PUBLICATION_EDITION = "2026-10-25"
PDF = f"assets/docs/manuals/industrial-solutions-user-manual-{EDITION}.pdf"
PPTX = f"assets/docs/manuals/industrial-solutions-user-manual-{EDITION}.pptx"
CHAPTERS = [
    ("01-plc", "plc", "plc-simulation.html"),
    ("02-gateway", "gateway", "iiot-gateway.html"),
    ("03-twin", "twin", "twinforge.html"),
    ("04-oee", "oee", "oee-analyzer.html"),
    ("05-data", "data", "datanexus-analytics.html"),
    ("06-assistant", "assistant", "industrial-ai-assistant.html"),
    ("07-assethub", "assethub", "industrial-assethub.html"),
]
SAMPLES = [
    ("manual-process.csv", "data", "CSV 가져오기 실습 파일", "교육용 가상 데이터 3행입니다."),
    ("twin-robot-filtered.csv", "twin", "TwinForge 필터 CSV 예시", "로컬 모의 공장 화면에서 저장한 로봇 설비 100행입니다."),
    ("analytics-temperature.csv", "data", "분석 그리드 CSV 예시", "로컬 분석 그리드에서 저장한 Temperature 실습 데이터 3행입니다."),
    ("analytics-temperature.json", "data", "분석 그리드 JSON 예시", "같은 실습 데이터의 JSON 3개 레코드입니다."),
    ("assistant-conversation.md", "assistant", "Assistant 대화 내보내기 예시", "Fake 생성과 실제 PLC 읽기 출처가 표시된 로컬 대화 기록입니다. 인증 키는 포함하지 않습니다."),
]


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def copy_checked(source: Path, destination: Path, expected_sha: str | None = None):
    actual = sha256(source)
    if expected_sha and actual != expected_sha:
        raise ValueError(f"Reviewed evidence hash mismatch: {source.name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)
    if sha256(destination) != actual:
        raise ValueError(f"Copy verification failed: {destination.name}")
    return actual


def markdown_copy(source: Path, destination: Path, screenshot_map: dict[str, str], refresh_notes=None, prerequisites=None):
    text = source.read_text(encoding="utf-8-sig")
    if prerequisites:
        original, current = prerequisites
        assert len(original) == len(current)
        for before, after in zip(original, current):
            assert "- " + before in text
            text = text.replace("- " + before, "- " + after, 1)
    if refresh_notes:
        sections = re.split(r"(?=^## \d+\.)", text, flags=re.M)
        for index, section in enumerate(sections):
            for filename, refresh in refresh_notes.items():
                if f"../assets/screenshots/{filename}" not in section:
                    continue
                observed = refresh["evidence"]["observed"].replace("\n", " ")
                note = refresh.get("captureNote", f"{PUBLICATION_EDITION} 재촬영. {observed}")
                section = re.sub(r"^관측 결과:.*$", lambda _: "관측 결과: " + observed, section, flags=re.M)
                section = re.sub(r"^캡처 안내:.*$", lambda _: "캡처 안내: " + note, section, flags=re.M)
                section = re.sub(r"^검증 범위:.*$", lambda _: "검증 범위: " + note, section, flags=re.M)
                if refresh.get("currentSteps"):
                    numbered = list(re.finditer(r"^\d+\. .*(?:\n|$)", section, flags=re.M))
                    assert numbered, "Current steps require an existing procedure block"
                    current = "\n".join(f"{i}. {step}" for i, step in enumerate(refresh["currentSteps"], 1)) + "\n"
                    section = section[:numbered[0].start()] + current + section[numbered[-1].end():]
                    expected = refresh.get("currentExpected", refresh.get("resultShort", note))
                    section = re.sub(r"^기대 결과:.*$", lambda _: "기대 결과: " + expected, section, flags=re.M)
                    if refresh.get("legacyEvidenceNote"):
                        section = section.rstrip() + "\n\n이전 자료 안내: " + refresh["legacyEvidenceNote"] + "\n\n"
            sections[index] = section
        text = "".join(sections)

    def replace_link(match):
        target = match.group(2)
        if target.startswith("../assets/screenshots/"):
            output = ROOT / screenshot_map[Path(target).name]
        elif target.startswith("../samples/"):
            output = ROOT / "assets/docs/manuals/samples" / Path(target).name
        else:
            return match.group(0)
        relative = os.path.relpath(output, destination.parent).replace("\\", "/")
        return match.group(1) + relative + match.group(3)

    text = re.sub(r"(!?\[[^\]]*\]\()([^\)]+)(\))", replace_link, text)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8", newline="\n")
    for link in re.findall(r"!?\[[^\]]*\]\(([^\)]+)\)", text):
        if re.match(r"^[a-z][a-z0-9+.-]*:", link, flags=re.I) or link.startswith("#"):
            continue
        if not (destination.parent / link.split("#", 1)[0]).resolve().is_file():
            raise ValueError(f"Broken copied Markdown link in {destination.name}: {link}")


def capture_notes(text: str) -> dict[str, str]:
    return {
        name: note.strip()
        for name, note in re.findall(
            r"!\[[^\]]*\]\(\.\./assets/screenshots/([^\)]+)\)\s*\n\s*캡처 안내:\s*([^\n]+)",
            text,
        )
    }


def publication_assets(manifest_path: Path | None):
    """Copy only the reviewed publication artifacts, retaining old public URLs."""
    if not manifest_path or not manifest_path.is_file():
        return None, None
    raw = read_json(manifest_path)
    edition = raw["edition"]
    assert edition == PUBLICATION_EDITION and raw["sourceEdition"] == EDITION
    assert {item["id"] for item in raw["solutions"]} == {item[1] for item in CHAPTERS}

    def publish(entry, identity):
        result = {k: entry[k] for k in ("id", "label", "slides", "chapterPage", "prerequisitesPage", "resourcesPage", "operationPages") if k in entry}
        for extension in ("pdf", "pptx"):
            artifact = entry[extension]
            origin = Path(artifact["path"])
            if not origin.is_absolute():
                origin = manifest_path.parent / origin
            public = (f"assets/docs/manuals/industrial-solutions-user-manual-{edition}.{extension}" if identity == "integrated"
                      else f"assets/docs/manuals/solutions/{identity}-user-manual-{edition}.{extension}")
            digest = copy_checked(origin, ROOT / public, artifact["sha256"])
            assert (ROOT / public).stat().st_size == artifact["bytes"]
            result[extension] = {"path": public, "bytes": artifact["bytes"], "sha256": digest, "pages": entry["slides"]}
        return result

    public = {"edition": edition, "sourceEdition": raw["sourceEdition"], "sourceManifestSha256": sha256(manifest_path),
              "integrated": publish(raw["integrated"], "integrated"),
              "solutions": [publish(item, item["id"]) for item in raw["solutions"]]}
    public["legacyDownloads"] = {}
    for extension in ("pdf", "pptx"):
        legacy = f"assets/docs/manuals/industrial-solutions-user-manual-{EDITION}.{extension}"
        copy_checked(ROOT / public["integrated"][extension]["path"], ROOT / legacy, public["integrated"][extension]["sha256"])
        public["legacyDownloads"][extension] = legacy
    write_json(ROOT / "content/manual-publication.json", public)
    return public, raw


def capture_overrides(manifest_path, publication_raw, explicit):
    value = explicit or ((publication_raw or {}).get("captureOverrides"))
    if not value:
        return {}, None, {}
    if isinstance(value, dict):
        return value.get("operations", value), manifest_path.parent, value.get("productOverrides", {})
    path = Path(value)
    if not path.is_absolute():
        path = manifest_path.parent / path
    payload = read_json(path)
    return payload.get("operations", payload), path.parent.parent if path.parent.name == "data" else path.parent, payload.get("productOverrides", {})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT.parent / "솔루션_사용매뉴얼" / EDITION)
    parser.add_argument("--publication-manifest", type=Path, default=ROOT.parent / "솔루션_사용매뉴얼" / PUBLICATION_EDITION / "publication-manifest.json")
    parser.add_argument("--capture-overrides", type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    publication, publication_raw = publication_assets(args.publication_manifest)
    overrides, override_root, product_overrides = capture_overrides(args.publication_manifest, publication_raw, args.capture_overrides)
    solution_documents = {item["id"]: item for item in publication["solutions"]} if publication else {}
    pdf_url = publication["integrated"]["pdf"]["path"] if publication else PDF
    pptx_url = publication["integrated"]["pptx"]["path"] if publication else PPTX
    manifest = read_json(source / "data/manual-manifest.json")
    visual = read_json(source / "data/visual-copy.json")
    icon_map = read_json(source / "assets/design/icon-map.json")
    icon_sources = read_json(source / "assets/design/icon-provenance.json")
    portfolio = {p["id"]: p for p in read_json(ROOT / "content/projects.json")["projects"]}
    operation_pages = {s["operation"]: s for s in manifest["slides"] if s.get("kind") == "operation"}
    chapter_pages = {s["chapter"]: s["number"] for s in manifest["slides"] if s.get("kind") == "chapter"}
    if len(manifest["slides"]) != 56 or len(operation_pages) != 41 or len(chapter_pages) != 7:
        raise ValueError("The final reviewed 56-page, 41-operation edition is required.")

    screenshot_map = {}
    screenshot_hashes = {}
    source_records = []
    chapter_sources = {}
    used_icons = set()
    products = []
    all_states = Counter()
    # Only the reviewed, public sample exports are copied; no runtime folder,
    # configuration, environment file, or credential store is read.
    samples = []
    for filename, product_id, label, note in SAMPLES:
        path = f"assets/docs/manuals/samples/{filename}"
        digest = copy_checked(source / "samples" / filename, ROOT / path)
        samples.append({"id": Path(filename).stem, "productId": product_id, "label": label, "note": note, "description": note, "kind": Path(filename).suffix.lstrip("."), "path": path, "sha256": digest})
        source_records.append({"kind": "sample", "source": f"samples/{filename}", "path": path, "sha256": digest})
    for identity, refresh in overrides.items():
        if not refresh.get("download"):
            continue
        item = refresh["download"]
        origin = override_root / item["path"]
        path = "assets/docs/manuals/samples/" + origin.name
        digest = copy_checked(origin, ROOT / path, item["sha256"])
        samples.append({"id": origin.stem, "productId": identity.split("-", 1)[0], "label": "DataNexus 보고서 실제 저장 파일", "note": "2026-10-25 Copy MD와 Download .md의 내용 일치를 확인한 로컬 템플릿 보고서입니다.", "description": "실행 검증에서 실제 저장한 보고서", "kind": "md", "path": path, "sha256": digest})
        source_records.append({"kind": "refreshed-sample", "sourceEdition": PUBLICATION_EDITION, "source": item["path"], "path": path, "sha256": digest})

    for source_id, product_id, portfolio_page in CHAPTERS:
        chapter = read_json(source / "data" / f"{source_id}.json")
        chapter_sources[source_id] = chapter
        for operation in chapter["operations"]:
            capture = operation.get("screenshot")
            if not capture:
                continue
            filename = Path(capture).name
            destination = f"assets/screenshots/manuals/{EDITION}/{filename}"
            digest = copy_checked(source / capture, ROOT / destination, operation["evidence"]["sha256"])
            screenshot_map[filename] = destination
            screenshot_hashes[destination] = digest
            source_records.append({"kind": "screenshot", "source": capture, "path": destination, "sha256": digest})

    for source_id, product_id, portfolio_page in CHAPTERS:
        chapter = chapter_sources[source_id]
        manifest_chapter = chapter["id"]
        summary = visual["chapters"][source_id]
        product_icon = icon_map["products"][product_id]
        used_icons.add(product_icon["file"])
        markdown_path = f"assets/docs/manuals/chapters/{product_id}.md"
        chapter_md = source / "chapters" / f"{source_id}.md"
        notes = capture_notes(chapter_md.read_text(encoding="utf-8-sig"))
        states = Counter()
        operations = []
        for order, original in enumerate(chapter["operations"], 1):
            operation_id = original["id"]
            brief = visual["operations"][operation_id]
            slide = operation_pages[operation_id]
            if slide["chapter"] != manifest_chapter:
                raise ValueError(f"Chapter mismatch for {operation_id}")
            stages = []
            for stage in brief["actionStages"]:
                icon_file = icon_map["semanticAliases"][stage["icon"]]
                used_icons.add(icon_file)
                stages.append({"icon": "assets/icons/lucide/" + Path(icon_file).name, "iconName": stage["icon"], "label": stage["label"], "detail": stage["detail"]})
            capture = original.get("screenshot")
            screenshot = screenshot_map[Path(capture).name] if capture else None
            evidence = original.get("evidence")
            state = brief["evidenceState"]
            states[state] += 1
            all_states[state] += 1
            aspect = slide.get("imageAspect", {})
            operations.append({
                "id": operation_id,
                "order": order,
                "title": original["title"],
                "shortTitle": brief["shortTitle"],
                "goal": original["goal"],
                "oneLineGoal": brief["oneLineGoal"],
                "stages": stages,
                "steps": original["steps"],
                "expected": original["expected"],
                "resultShort": brief["resultShort"],
                "troubleshooting": original["troubleshooting"],
                "cautionShort": brief["cautionShort"],
                "evidenceState": state,
                "verified": original["verified"],
                "pdfPage": slide["number"],
                "pdfUrl": f"{pdf_url}#page={slide['number']}",
                "screenshot": screenshot,
                "screenshotWidth": aspect.get("sourceWidth"),
                "screenshotHeight": aspect.get("sourceHeight"),
                "captureNote": notes.get(Path(capture).name) if capture else None,
                "evidence": evidence,
                "focus": slide.get("focus"),
                "focusTargets": brief.get("focus", {}).get("targetNames", []),
            })
            operation = operations[-1]
            if product_id in solution_documents:
                document = solution_documents[product_id]
                operation["standalonePdfPage"] = document["operationPages"][operation_id]
                operation["standalonePdfUrl"] = f"{document['pdf']['path']}#page={operation['standalonePdfPage']}"
            if operation_id in overrides:
                refresh = overrides[operation_id]
                capture_path = Path(refresh["screenshot"])
                if not capture_path.is_absolute():
                    capture_path = override_root / capture_path
                destination = f"assets/screenshots/manuals/{PUBLICATION_EDITION}/{capture_path.name}"
                digest = copy_checked(capture_path, ROOT / destination, refresh["evidence"]["sha256"])
                operation["originalEvidence"] = operation["evidence"]
                operation["originalScreenshot"] = operation["screenshot"]
                operation["screenshot"] = destination
                operation["evidence"] = refresh["evidence"]
                operation["screenshotWidth"] = refresh.get("width", refresh.get("screenshotWidth", operation["screenshotWidth"]))
                operation["screenshotHeight"] = refresh.get("height", refresh.get("screenshotHeight", operation["screenshotHeight"]))
                for field in ("captureNote", "cautionShort", "resultShort", "evidenceState"):
                    if field in refresh:
                        operation[field] = refresh[field]
                if refresh.get("actionStages"):
                    current_stages = []
                    for stage in refresh["actionStages"]:
                        icon_file = icon_map["semanticAliases"][stage["icon"]]
                        used_icons.add(icon_file)
                        current_stages.append({"icon": "assets/icons/lucide/" + Path(icon_file).name, "iconName": stage["icon"], "label": stage["label"], "detail": stage["detail"]})
                    operation["stages"] = current_stages
                if refresh.get("currentSteps"):
                    operation["originalSteps"] = operation["steps"]
                    operation["originalExpected"] = operation["expected"]
                    operation["steps"] = refresh["currentSteps"]
                    operation["expected"] = refresh.get("currentExpected", refresh.get("resultShort", refresh["captureNote"]))
                if refresh.get("legacyEvidenceNote"):
                    operation["legacyEvidenceNote"] = refresh["legacyEvidenceNote"]
                if operation["evidenceState"] != state:
                    states[state] -= 1; all_states[state] -= 1
                    states[operation["evidenceState"]] += 1; all_states[operation["evidenceState"]] += 1
                operation["captureRefresh"] = {"edition": PUBLICATION_EDITION, "sha256": digest}
                screenshot_map[Path(capture).name] = destination
                source_records.append({"kind": "refreshed-screenshot", "sourceEdition": PUBLICATION_EDITION, "source": capture_path.relative_to(override_root).as_posix(), "path": destination, "sha256": digest})
        refreshed_notes = {Path(op["screenshot"]).name: overrides[op["id"]] for op in chapter["operations"] if op["id"] in overrides}
        current_prerequisites = product_overrides.get(product_id, {}).get("prerequisites", chapter["prerequisites"])
        markdown_copy(chapter_md, ROOT / markdown_path, screenshot_map, refreshed_notes, (chapter["prerequisites"], current_prerequisites) if current_prerequisites != chapter["prerequisites"] else None)
        first_capture = next((o["screenshot"] for o in operations if o["screenshot"]), None)
        product = {
            "id": product_id,
            "sourceId": source_id,
            "manifestChapterId": manifest_chapter,
            "order": len(products) + 1,
            "label": portfolio[product_id]["label"],
            "title": chapter["title"],
            "shortTitle": summary["shortTitle"],
            "subtitle": summary["subtitle"],
            "scope": chapter["scope"],
            "scopeNote": summary["scopeNote"],
            "prerequisites": current_prerequisites,
            "actions": summary["actions"],
            "icon": "assets/icons/lucide/" + Path(product_icon["file"]).name,
            "accent": product_icon["accent"],
            "portfolioPage": portfolio_page,
            "manualPage": f"manual-{product_id}.html",
            "chapterPdfPage": chapter_pages[manifest_chapter],
            "pdfPageStart": chapter_pages[manifest_chapter],
            "pdfPageEnd": operations[-1]["pdfPage"],
            "pdfUrl": f"{pdf_url}#page={chapter_pages[manifest_chapter]}",
            "markdown": markdown_path,
            "screenshot": first_capture,
            "counts": {"operations": len(operations), "screenshots": sum(bool(o["screenshot"]) for o in operations), "full": states["full"], "partial": states["partial"], "unverified": states["unverified"]},
            "samples": [s for s in samples if s["productId"] == product_id],
            "localUrl": chapter["url"],
            "sources": chapter.get("sources", []),
            "operations": operations,
        }
        if product_id in solution_documents:
            document = solution_documents[product_id]
            product["downloads"] = {extension: document[extension]["path"] for extension in ("pdf", "pptx")}
            product["standalonePages"] = document["slides"]
        if current_prerequisites != chapter["prerequisites"]:
            product["originalPrerequisites"] = chapter["prerequisites"]
        products.append(product)

    # Shared interface controls, in addition to each product and action icon.
    used_icons.update(f"icons/{name}.svg" for name in ["book-open", "file-down", "file-text", "search", "check-circle", "alert-triangle", "info", "external-link", "chevron-right"])
    selected_sources = []
    for record in icon_sources["assets"]:
        if record["file"] not in used_icons:
            continue
        path = "assets/icons/lucide/" + Path(record["file"]).name
        digest = copy_checked(source / "assets/design" / record["file"], ROOT / path, record["sha256"])
        selected_sources.append({**record, "file": Path(record["file"]).name, "path": path})
        source_records.append({"kind": "icon", "source": "assets/design/" + record["file"], "path": path, "sha256": digest})
    if len(selected_sources) != len(used_icons):
        raise ValueError("A required icon has no reviewed source record.")
    copy_checked(source / "assets/design/LICENSE-Lucide.txt", ROOT / "assets/icons/lucide/LICENSE-Lucide.txt")
    write_json(ROOT / "assets/icons/lucide/icon-provenance.json", {k: v for k, v in icon_sources.items() if k != "assets"} | {"assets": selected_sources})
    (ROOT / "assets/icons/lucide/SOURCES.md").write_text(
        "# Lucide icon sources\n\n"
        f"This public portfolio uses {len(selected_sources)} original SVG icons from the official "
        f"[Lucide repository]({icon_sources['repository']}).\n\n"
        f"Pinned commit: `{icon_sources['commit']}`. Original geometry, viewBox and currentColor are preserved.\n\n"
        "- [Per-file source URLs and SHA-256 values](icon-provenance.json)\n"
        "- [Complete upstream ISC and Feather-derived MIT license](LICENSE-Lucide.txt)\n\n"
        "These icons support navigation and instructions. They do not replace captured evidence.\n",
        encoding="utf-8", newline="\n",
    )
    if len(screenshot_hashes) != 38 or sum(all_states.values()) != 41 or all_states["unverified"] != 3:
        raise ValueError("Reviewed evidence coverage changed.")
    public = {
        "schemaVersion": 2 if publication else 1,
        "date": publication["edition"] if publication else EDITION,
        "sourceEdition": EDITION,
        "title": "산업 솔루션 사용 매뉴얼",
        "scope": "로컬 개발 환경에서 촬영한 7개 솔루션의 41개 동작입니다. 각 절차의 확인 범위와 데이터 출처를 함께 읽습니다. 문제 해결 분기 전체의 실행을 뜻하지 않습니다.",
        "evidenceLegend": visual["evidenceLegend"],
        "downloads": {"pdf": pdf_url, "pptx": pptx_url},
        "stats": {"products": len(products), "operations": len(operation_pages), "screenshots": len(screenshot_hashes), "pdfPages": len(manifest["slides"]), "full": all_states["full"], "partial": all_states["partial"], "unverified": all_states["unverified"], "icons": len(selected_sources)},
        "iconLicense": "assets/icons/lucide/LICENSE-Lucide.txt",
        "iconSources": "assets/icons/lucide/SOURCES.md",
        "samples": samples,
        "products": products,
    }
    if publication:
        public["publication"] = "content/manual-publication.json"
        public["legacyDownloads"] = publication["legacyDownloads"]
        public["stats"]["downloadFiles"] = 16
        publication["captureRefresh"] = [{"id": operation["id"], "screenshot": operation["screenshot"], "evidence": operation["evidence"], "evidenceState": operation["evidenceState"], "captureNote": operation["captureNote"], **({"currentSteps": operation["steps"], "currentExpected": operation["expected"], "stages": operation["stages"], "legacyEvidenceNote": operation.get("legacyEvidenceNote")} if operation.get("originalSteps") else {})} for product in products for operation in product["operations"] if operation.get("captureRefresh")]
        publication["productOverrides"] = product_overrides
        write_json(ROOT / "content/manual-publication.json", publication)
    write_json(ROOT / "content/manuals.json", public)
    write_json(ROOT / "content/manual-assets.json", {"schemaVersion": 2 if publication else 1, "date": public["date"], "sourceEdition": EDITION, "sourceManifestSha256": sha256(source / "data/manual-manifest.json"), "files": source_records})
    print(json.dumps({"output": "content/manuals.json", "stats": public["stats"], "chapters": [{"id": p["id"], "start": p["pdfPageStart"], "end": p["pdfPageEnd"]} for p in products]}, ensure_ascii=True))


if __name__ == "__main__":
    main()
