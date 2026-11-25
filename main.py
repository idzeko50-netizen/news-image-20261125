#!/usr/bin/env python3
"""Copy entry/entry.png to MAKEFUN_OUTPUT_DIR/entry.png and verify it.

Stdlib only, no network. Verifies the PNG magic bytes, the IHDR chunk
(dimensions 1024x1024), the file size and the SHA-256 of the copy, then
chmods the output 0644.
"""

import hashlib
import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "entry", "entry.png")
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_dimensions(path):
    with open(path, "rb") as handle:
        header = handle.read(33)
    if header[:8] != PNG_MAGIC:
        raise ValueError("not a PNG: bad magic bytes")
    length, chunk_type = struct.unpack(">I4s", header[8:16])
    if chunk_type != b"IHDR" or length != 13:
        raise ValueError("not a PNG: first chunk is not a 13-byte IHDR")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def main():
    if not os.path.isfile(SOURCE):
        raise FileNotFoundError("missing source image: %s" % SOURCE)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(SOURCE, dest)
    width, height = read_dimensions(dest)
    if (width, height) != (1024, 1024):
        raise ValueError(
            "unexpected dimensions %dx%d, expected 1024x1024"
            % (width, height)
        )
    size = os.path.getsize(dest)
    if size != os.path.getsize(SOURCE):
        raise ValueError("copy size %d differs from source" % size)
    if size > MAX_BYTES:
        raise ValueError("entry.png is %d bytes, over the 1 MiB limit" % size)
    digest = sha256_of(dest)
    if digest != sha256_of(SOURCE):
        raise ValueError("SHA-256 mismatch between source and copy")
    os.chmod(dest, 0o644)
    print("entry.png: %dx%d, %d bytes, sha256 %s" % (width, height, size, digest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
