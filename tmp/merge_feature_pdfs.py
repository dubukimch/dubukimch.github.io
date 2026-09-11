from pathlib import Path

from pypdf import PdfReader, PdfWriter


root = Path(__file__).resolve().parents[1]
inputs = [
    ("PLC Simulation", root / "tmp" / "pdfs" / "plc-v2.pdf"),
    ("IIoT Gateway", root / "tmp" / "pdfs" / "gateway-v2.pdf"),
    ("TwinForge", root / "tmp" / "pdfs" / "twinforge-v2.pdf"),
]
output = root / "assets" / "docs" / "industrial-products-feature-guide.pdf"

writer = PdfWriter()
page_offset = 0
counts = []
for title, path in inputs:
    reader = PdfReader(path)
    counts.append((title, len(reader.pages)))
    for page in reader.pages:
        writer.add_page(page)
    writer.add_outline_item(title, page_number=page_offset)
    page_offset += len(reader.pages)

writer.add_metadata(
    {
        "/Title": "Industrial Products Feature Guide",
        "/Author": "Dubu Kim",
        "/Subject": "PLC Simulation, IIoT Gateway, TwinForge product UI workflows",
    }
)
with output.open("wb") as stream:
    writer.write(stream)

print(f"output={output}")
print(f"pages={page_offset}")
for title, count in counts:
    print(f"{title}={count}")
