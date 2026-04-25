from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "assets" / "tutorials" / "constraints"
SOURCE_SHEET = OUT_DIR / "constraint_imagegen_source_sheet.png"
CARD_WIDTH = 320
CARD_HEIGHT = 260


ITEMS = [
    ("position", "Position", "Copies location only"),
    ("rotation", "Rotation", "Copies turning only"),
    ("scale", "Scale", "Copies size changes"),
    ("aim", "Aim", "Points object at target"),
    ("parentchild", "Parent-Child", "Follows parent space"),
    ("relation", "Relation", "Logic boxes drive values"),
    ("chainik", "Chain IK", "IK handle bends chain"),
    ("splineik", "Spline IK", "Curve bends chain"),
    ("path", "Path", "Object follows path"),
    ("expression", "Expression", "Formula drives motion"),
    ("range", "Range", "Limits or remaps values"),
    ("mapping", "Mapping", "Maps one rig to another"),
    ("multireferential", "Multi-Referential", "Switches parent spaces"),
    ("threepoints", "Three Points", "Builds plane from 3 markers"),
    ("rigidbody", "Rigid Body", "Physics collision style"),
]


def card_bounds(sheet_width: int, sheet_height: int, index: int):
    cols = 5
    rows = 3
    col = index % cols
    row = index // cols
    margin_x = int(round(sheet_width * 0.012))
    margin_y = int(round(sheet_height * 0.020))
    gutter_x = int(round(sheet_width * 0.012))
    gutter_y = int(round(sheet_height * 0.024))
    card_w = int(round((sheet_width - margin_x * 2 - gutter_x * (cols - 1)) / cols))
    card_h = int(round((sheet_height - margin_y * 2 - gutter_y * (rows - 1)) / rows))
    left = margin_x + col * (card_w + gutter_x)
    top = margin_y + row * (card_h + gutter_y)
    return (left, top, left + card_w, top + card_h)


def fit_card(image: Image.Image):
    image = image.convert("RGB")
    fitted = ImageOps.contain(image, (CARD_WIDTH, CARD_HEIGHT), method=Image.Resampling.LANCZOS)
    background = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), (4, 10, 14))
    offset = ((CARD_WIDTH - fitted.width) // 2, (CARD_HEIGHT - fitted.height) // 2)
    background.paste(fitted, offset)
    return background


def main():
    if not SOURCE_SHEET.exists():
        raise SystemExit("Missing source sheet: {0}".format(SOURCE_SHEET))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sheet = Image.open(SOURCE_SHEET)
    index = {}
    for item_index, (key, title, description) in enumerate(ITEMS):
        crop = sheet.crop(card_bounds(sheet.width, sheet.height, item_index))
        path = OUT_DIR / "{0}.png".format(key)
        fit_card(crop).save(path, "PNG", optimize=True)
        index[key] = {"title": title, "description": description, "file": path.name}
    (OUT_DIR / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8", newline="\n")
    print("Generated {0} static constraint tutorial images in {1}".format(len(index), OUT_DIR))


if __name__ == "__main__":
    main()
