#!/usr/bin/env python3
"""Create a monster template ZIP from a directory with template.json and images/."""

import json
import zipfile
import sys
from pathlib import Path


def build_monster_template_zip(source_dir: str, output_path: str) -> str:
    src = Path(source_dir)
    if not src.is_dir():
        raise NotADirectoryError(f"Source directory not found: {source_dir}")

    template_json = src / "template.json"
    if not template_json.exists():
        raise FileNotFoundError(f"template.json not found in {source_dir}")

    images_dir = src / "images"
    if not images_dir.is_dir():
        raise NotADirectoryError(f"images/ directory not found in {source_dir}")

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(template_json, "template.json")
        for img in sorted(images_dir.iterdir()):
            if img.is_file() and img.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                zf.write(img, f"images/{img.name}")

    return str(out.resolve())


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: build_zip.py <source_dir> [output_path]")
        sys.exit(1)

    src = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else f"{src.rstrip('/')}.zip"
    path = build_monster_template_zip(src, out)
    print(path)
