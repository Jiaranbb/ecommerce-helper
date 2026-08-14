#!/usr/bin/env python3
"""Normalize a folder of raster pages to one exact size without stretching."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Center-crop and scale product-detail pages to an exact size."
    )
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1440)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing existing PNG files in the output directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.width <= 0 or args.height <= 0 or args.width > 32768 or args.height > 32768:
        raise SystemExit("width and height must be between 1 and 32768")
    if not args.input_dir.is_dir():
        raise SystemExit(f"input directory not found: {args.input_dir}")

    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    if input_dir == output_dir:
        raise SystemExit("input and output directories must be different")

    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise SystemExit("ffmpeg is required but was not found in PATH")

    files = sorted(
        path for path in args.input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in EXTENSIONS
    )
    if not files:
        raise SystemExit(f"no supported images found in: {args.input_dir}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    destinations = [args.output_dir / f"{source.stem}.png" for source in files]
    existing = [path for path in destinations if path.exists()]
    if existing and not args.overwrite:
        preview = ", ".join(path.name for path in existing[:5])
        suffix = "..." if len(existing) > 5 else ""
        raise SystemExit(
            f"output files already exist: {preview}{suffix}; pass --overwrite to replace them"
        )
    ratio = args.width / args.height
    vf = (
        f"crop='if(gt(iw/ih,{ratio}),ih*{ratio},iw)':"
        f"'if(gt(iw/ih,{ratio}),ih,iw/{ratio})',"
        f"scale={args.width}:{args.height}:flags=lanczos"
    )

    for source, destination in zip(files, destinations):
        subprocess.run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y" if args.overwrite else "-n",
                "-i",
                str(source),
                "-vf",
                vf,
                str(destination),
            ],
            check=True,
        )
        print(destination)

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"ffmpeg failed with exit code {exc.returncode}", file=sys.stderr)
        raise SystemExit(exc.returncode) from exc
