#!/usr/bin/env python3
"""Report eCommerce-helper runtime availability without installing anything."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


CHROME_COMMANDS = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "microsoft-edge",
    "msedge",
)

MACOS_CHROME_PATHS = (
    Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
    Path("/Applications/Chromium.app/Contents/MacOS/Chromium"),
    Path("/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"),
)


def find_chrome() -> str:
    explicit = os.environ.get("ECOMMERCE_HELPER_CHROME", "").strip()
    if explicit and Path(explicit).is_file():
        return explicit
    for command in CHROME_COMMANDS:
        resolved = shutil.which(command)
        if resolved:
            return resolved
    for path in MACOS_CHROME_PATHS:
        if path.is_file():
            return str(path)
    windows_roots = [
        os.environ.get("PROGRAMFILES", ""),
        os.environ.get("PROGRAMFILES(X86)", ""),
        os.environ.get("LOCALAPPDATA", ""),
    ]
    suffixes = (
        Path("Google/Chrome/Application/chrome.exe"),
        Path("Chromium/Application/chrome.exe"),
        Path("Microsoft/Edge/Application/msedge.exe"),
    )
    for root in filter(None, windows_roots):
        for suffix in suffixes:
            candidate = Path(root) / suffix
            if candidate.is_file():
                return str(candidate)
    return ""


def weasyprint_usable() -> bool:
    if importlib.util.find_spec("weasyprint") is None:
        return False
    result = subprocess.run(
        [sys.executable, "-c", "from weasyprint import HTML"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check eCommerce-helper dependencies without modifying the system."
    )
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return non-zero unless PDF rendering and image normalization are ready.",
    )
    args = parser.parse_args()

    python_ok = sys.version_info >= (3, 9)
    markdown_ok = importlib.util.find_spec("markdown") is not None
    chrome = find_chrome()
    weasy_ok = weasyprint_usable() if not chrome else False
    ffmpeg = shutil.which("ffmpeg") or ""
    pdf_ready = python_ok and markdown_ok and bool(chrome or weasy_ok)
    image_normalization_ready = bool(ffmpeg)
    overall = "ready" if pdf_ready and image_normalization_ready else "partial"

    result = {
        "status": overall,
        "python": {
            "ok": python_ok,
            "version": ".".join(map(str, sys.version_info[:3])),
            "minimum": "3.9",
        },
        "pdf": {
            "ready": pdf_ready,
            "markdown_module": markdown_ok,
            "chrome": chrome or None,
            "weasyprint_fallback": weasy_ok,
        },
        "image_normalization": {
            "ready": image_normalization_ready,
            "ffmpeg": ffmpeg or None,
        },
        "optional_qa": {
            "pdfinfo": shutil.which("pdfinfo"),
            "pdftoppm": shutil.which("pdftoppm"),
            "pypdf_module": importlib.util.find_spec("pypdf") is not None,
        },
        "notes": [
            "This command only inspects the current environment; it does not install dependencies.",
            "Research and copywriting can continue when media tools are missing; report the unavailable deliverables clearly.",
        ],
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"eCommerce-helper environment: {overall.upper()}")
        print(f"Python >= 3.9: {'OK' if python_ok else 'MISSING'} ({result['python']['version']})")
        print(f"Markdown module: {'OK' if markdown_ok else 'MISSING'}")
        print(f"PDF renderer: {'OK' if pdf_ready else 'MISSING'}")
        print(f"  Chrome/Chromium: {chrome or 'not found'}")
        print(f"  WeasyPrint fallback: {'OK' if weasy_ok else 'not available'}")
        print(f"Image normalization (ffmpeg): {ffmpeg or 'not found'}")
        print("No dependencies were installed or changed.")

    if args.strict and not (pdf_ready and image_normalization_ready):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
