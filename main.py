#!/usr/bin/env python3
"""Entry point for the make.fun news-image-20261125 entry.

Stdlib only: copies the pre-rendered entry.png (produced by draw_image.py)
into the output directory. Renders nothing at grade time — the grader's
pinned python:3.13 image has no PIL and no fonts, so this file must not
import anything beyond the standard library.
"""
import hashlib
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "entry.png")
    shutil.copyfile(src, dst)
    os.chmod(dst, 0o644)
    with open(src, "rb") as f:
        want = hashlib.sha256(f.read()).hexdigest()
    with open(dst, "rb") as f:
        got = hashlib.sha256(f.read()).hexdigest()
    if want != got:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
