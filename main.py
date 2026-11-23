#!/usr/bin/env python3
"""news-image-20261123 entrypoint.

Copies the pre-rendered entry.png (Monday 23 November 2026 world news,
one image, 1024x1024, under 1 MiB) to the output directory and validates
it. Standard library only; no network; deterministic: the same bytes are
written on every run.
"""
import hashlib
import os
import shutil
import struct
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry.png")
MAX_BYTES = 1048576
EXPECT_W = 1024
EXPECT_H = 1024


def output_dir():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out:
        return out
    return tempfile.mkdtemp(prefix="makefun-output-")


def check_png(path):
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) > MAX_BYTES:
        raise SystemExit("entry.png over 1 MiB: %d bytes" % len(data))
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("entry.png is not a PNG")
    if b"IHDR" not in data[:32] or not data.rstrip().endswith(b"IEND\xaeB`\x82"):
        raise SystemExit("entry.png is truncated: missing IHDR or IEND")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (EXPECT_W, EXPECT_H):
        raise SystemExit("entry.png is %dx%d, want 1024x1024" % (width, height))
    return data


def main():
    data = check_png(SOURCE)
    out = output_dir()
    os.makedirs(out, exist_ok=True)
    dest = os.path.join(out, "entry.png")
    shutil.copyfile(SOURCE, dest)
    with open(dest, "rb") as fh:
        copied = fh.read()
    if hashlib.sha256(copied).hexdigest() != hashlib.sha256(data).hexdigest():
        raise SystemExit("copy mismatch")
    print("wrote %s (%d bytes, sha256 %s)"
          % (dest, len(copied), hashlib.sha256(copied).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
