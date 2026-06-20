"""CLI: ``python -m iris.gallery build -o _site``."""

from __future__ import annotations

import argparse
import sys

from .build import build


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="iris.gallery")
    sub = parser.add_subparsers(dest="command", required=True)

    build_cmd = sub.add_parser("build", help="render the gallery to static HTML")
    build_cmd.add_argument("-o", "--out", default="_site", help="output directory")

    args = parser.parse_args(argv)
    if args.command == "build":
        path = build(args.out)
        print(f"wrote {path}")
        return 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
