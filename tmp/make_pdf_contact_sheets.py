from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFont


root = Path(__file__).resolve().parents[1]
prefix = sys.argv[1] if len(sys.argv) > 1 else "feature-v2-page"
pages = sorted((root / "tmp" / "pdfs").glob(f"{prefix}-*.png"))
out_dir = root / "tmp" / "pdfs" / f"contact-{prefix}"
out_dir.mkdir(parents=True, exist_ok=True)
font = ImageFont.load_default(size=20)

for batch_index in range(0, len(pages), 8):
    batch = pages[batch_index : batch_index + 8]
    sheet = Image.new("RGB", (1440, 1040), "#d9dde0")
    draw = ImageDraw.Draw(sheet)
    for slot, path in enumerate(batch):
        image = Image.open(path).convert("RGB")
        image.thumbnail((340, 480))
        x = 10 + (slot % 4) * 360
        y = 35 + (slot // 4) * 510
        page_number = batch_index + slot + 1
        draw.text((x, 8 + (slot // 4) * 510), f"PAGE {page_number:02d}", fill="#17212b", font=font)
        sheet.paste(image, (x, y))
    output = out_dir / f"contact-{batch_index // 8 + 1:02d}.jpg"
    sheet.save(output, quality=92)
    print(output)
