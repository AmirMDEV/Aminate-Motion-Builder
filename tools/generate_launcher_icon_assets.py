from __future__ import annotations

import base64
from pathlib import Path

from PIL import Image


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_PNG = Path(
    r"C:\Users\Amir Mansaray\.codex\generated_images\019d5c49-d7ef-7fe0-b0b5-582b1ff3ead0\ig_0776caa3615d9a7a0169e7f5075df88191b9e7556a7ce78846.png"
)
FULL_PNG = REPO_ROOT / "Aminate_Mobu_Logo_Full.png"
FULL_SVG = REPO_ROOT / "Aminate_Mobu_Logo_Full.svg"
ASSET_DIR = REPO_ROOT / "assets" / "icons"
SIZES = (16, 18, 32, 64)


def main() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    payload = SOURCE_PNG.read_bytes()
    FULL_PNG.write_bytes(payload)

    image = Image.open(SOURCE_PNG).convert("RGBA")
    for size in SIZES:
        image.resize((size, size), Image.LANCZOS).save(
            ASSET_DIR / f"aminate_toolbar_{size}.png"
        )

    encoded = base64.b64encode(payload).decode("ascii")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{image.width}" '
        f'height="{image.height}" viewBox="0 0 {image.width} {image.height}">\n'
        f'  <image width="{image.width}" height="{image.height}" '
        f'href="data:image/png;base64,{encoded}" />\n'
        f"</svg>\n"
    )
    FULL_SVG.write_text(svg, encoding="utf-8")

    print(FULL_PNG)
    print(FULL_SVG)


if __name__ == "__main__":
    main()
