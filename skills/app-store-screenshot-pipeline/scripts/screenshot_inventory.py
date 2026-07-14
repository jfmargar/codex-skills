#!/usr/bin/env python3
"""Inventory PNG screenshots and report dimensions without external deps."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def png_size(path: Path) -> tuple[int, int]:
    with path.open("rb") as handle:
        signature = handle.read(8)
        if signature != PNG_SIGNATURE:
            raise ValueError("not a PNG")
        length_bytes = handle.read(4)
        chunk_type = handle.read(4)
        if len(length_bytes) != 4 or chunk_type != b"IHDR":
            raise ValueError("missing IHDR")
        length = struct.unpack(">I", length_bytes)[0]
        data = handle.read(length)
        if len(data) < 8:
            raise ValueError("invalid IHDR")
        width, height = struct.unpack(">II", data[:8])
        return width, height


def inventory(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*.png")):
        try:
            width, height = png_size(path)
            status = "ok"
            error = None
        except Exception as exc:  # noqa: BLE001 - report all validation failures.
            width = height = 0
            status = "error"
            error = str(exc)
        rows.append(
            {
                "path": str(path),
                "relativePath": str(path.relative_to(root)),
                "width": width,
                "height": height,
                "status": status,
                "error": error,
            }
        )
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    rows = inventory(args.root)
    if args.as_json:
        print(json.dumps(rows, indent=2))
    else:
        for row in rows:
            if row["status"] == "ok":
                print(f'{row["relativePath"]}: {row["width"]}x{row["height"]}')
            else:
                print(f'{row["relativePath"]}: ERROR {row["error"]}')
    return 1 if any(row["status"] != "ok" for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
