from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "assets" / "tutorials" / "constraints"
WIDTH = 320
HEIGHT = 180


ITEMS = {
    "position": ("Position", "Copies location only"),
    "rotation": ("Rotation", "Copies turning only"),
    "scale": ("Scale", "Copies size changes"),
    "aim": ("Aim", "Points object at target"),
    "parentchild": ("Parent-Child", "Follows parent space"),
    "relation": ("Relation", "Logic boxes drive values"),
    "chainik": ("Chain IK", "IK handle bends chain"),
    "splineik": ("Spline IK", "Curve bends chain"),
    "path": ("Path", "Object follows path"),
    "expression": ("Expression", "Formula drives motion"),
    "range": ("Range", "Limits or remaps values"),
    "mapping": ("Mapping", "Maps one rig to another"),
    "multireferential": ("Multi-Referential", "Switches parent spaces"),
    "threepoints": ("3 Points", "Builds plane from 3 markers"),
    "rigidbody": ("Rigid Body", "Physics collision style"),
}


COLORS = {
    "bg": (25, 31, 38),
    "panel": (38, 47, 56),
    "blue": (88, 180, 230),
    "green": (90, 210, 150),
    "yellow": (240, 190, 74),
    "text": (235, 241, 246),
    "muted": (150, 162, 172),
    "line": (90, 105, 116),
}


def _fonts():
    try:
        return ImageFont.truetype("arial.ttf", 14), ImageFont.truetype("arial.ttf", 11)
    except Exception:
        fallback = ImageFont.load_default()
        return fallback, fallback


FONT, SMALL = _fonts()


def _box(draw, xy, text, fill):
    draw.rounded_rectangle(xy, radius=10, fill=fill, outline=COLORS["line"], width=2)
    center_x = int((xy[0] + xy[2]) * 0.5)
    center_y = int((xy[1] + xy[3]) * 0.5)
    width = draw.textlength(text, font=FONT)
    draw.text((center_x - width * 0.5, center_y - 8), text, fill=COLORS["text"], font=FONT)


def _draw_demo(key, title, subtitle, phase):
    image = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg"])
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((8, 8, WIDTH - 8, HEIGHT - 8), radius=14, fill=COLORS["panel"], outline=(64, 78, 90), width=2)
    draw.text((18, 15), title, fill=COLORS["text"], font=FONT)
    draw.text((18, 34), subtitle, fill=COLORS["muted"], font=SMALL)
    t = phase / 17.0

    if key in ("position", "parentchild", "mapping", "multireferential"):
        box_x = 190 + int(35 * math.sin(t * math.pi * 2))
        box_y = 92 + int(22 * math.cos(t * math.pi * 2))
        _box(draw, (40, 82, 100, 138), "Child", COLORS["blue"])
        _box(draw, (box_x - 34, box_y - 28, box_x + 34, box_y + 28), "Target", COLORS["green"])
        draw.line((100, 110, box_x - 34, box_y), fill=COLORS["yellow"], width=3)
    elif key in ("rotation", "aim"):
        _box(draw, (40, 82, 100, 138), "Obj", COLORS["blue"])
        target_x = 225
        target_y = 70 + int(55 * t)
        draw.ellipse((target_x - 15, target_y - 15, target_x + 15, target_y + 15), fill=COLORS["green"], outline=COLORS["line"], width=2)
        draw.line((100, 110, target_x, target_y), fill=COLORS["yellow"], width=4)
        draw.polygon([(target_x, target_y), (target_x - 10, target_y - 4), (target_x - 6, target_y + 8)], fill=COLORS["yellow"])
    elif key in ("scale", "range"):
        size = 34 + int(28 * t)
        _box(draw, (52 - size // 2, 110 - size // 2, 52 + size // 2, 110 + size // 2), "A", COLORS["blue"])
        _box(draw, (190, 82, 250, 138), "Driver", COLORS["green"])
        draw.line((85, 110, 190, 110), fill=COLORS["yellow"], width=3)
    elif key in ("chainik", "splineik"):
        points = [(55 + i * 45, 115 - int(math.sin(t * math.pi * 2 + i * 0.9) * 35)) for i in range(5)]
        draw.line(points, fill=COLORS["yellow"], width=5)
        for point in points:
            draw.ellipse((point[0] - 8, point[1] - 8, point[0] + 8, point[1] + 8), fill=COLORS["blue"])
        point = points[-1]
        draw.ellipse((point[0] - 13, point[1] - 13, point[0] + 13, point[1] + 13), outline=COLORS["green"], width=4)
    elif key == "path":
        path = [(40, 125), (95, 70), (155, 130), (230, 80), (285, 122)]
        draw.line(path, fill=COLORS["line"], width=4)
        point_x = 40 + int(245 * t)
        point_y = 105 + int(math.sin(t * math.pi * 4) * 32)
        draw.ellipse((point_x - 14, point_y - 14, point_x + 14, point_y + 14), fill=COLORS["blue"], outline=COLORS["green"], width=3)
    elif key == "expression":
        draw.text((40, 80), "Y = sin(frame) * 30", fill=COLORS["yellow"], font=FONT)
        point_y = 110 - int(math.sin(t * math.pi * 2) * 38)
        draw.ellipse((210 - 18, point_y - 18, 210 + 18, point_y + 18), fill=COLORS["blue"])
    elif key == "relation":
        for index, text in enumerate(["Input", "Math", "Output"]):
            _box(draw, (35 + index * 90, 85, 100 + index * 90, 135), text, [COLORS["blue"], COLORS["yellow"], COLORS["green"]][index])
        draw.line((100, 110, 125, 110), fill=COLORS["text"], width=3)
        draw.line((190, 110, 215, 110), fill=COLORS["text"], width=3)
    elif key == "threepoints":
        points = [(80, 125), (160, 65), (240, 125)]
        draw.polygon(points, fill=(58, 95, 115), outline=COLORS["yellow"])
        for point in points:
            draw.ellipse((point[0] - 9, point[1] - 9, point[0] + 9, point[1] + 9), fill=COLORS["green"])
    elif key == "rigidbody":
        point_y = 55 + int(65 * abs(math.sin(t * math.pi)))
        draw.rectangle((65, point_y, 110, point_y + 32), fill=COLORS["blue"], outline=COLORS["line"])
        draw.rectangle((45, 135, 270, 148), fill=COLORS["green"])

    return image


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index = {}
    for key, (title, subtitle) in ITEMS.items():
        frames = [_draw_demo(key, title, subtitle, phase) for phase in range(18)]
        path = OUT_DIR / "{0}.gif".format(key)
        frames[0].save(path, save_all=True, append_images=frames[1:], duration=70, loop=0, optimize=True)
        index[key] = {"title": title, "description": subtitle, "file": path.name}
    (OUT_DIR / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    print("Generated {0} constraint tutorial GIFs in {1}".format(len(index), OUT_DIR))


if __name__ == "__main__":
    main()
