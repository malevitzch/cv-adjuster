from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import cast

from achievements import mdify_achievements


class Arguments(Namespace):
    path: str
    outpath: str

    def __init__(self) -> None:
        super().__init__()
        self.path = ""
        self.outpath = ""


def main() -> None:
    parser = ArgumentParser()
    _ = parser.add_argument("path", help="The path to the source directory")
    _ = parser.add_argument("outpath", help="The path to the output directory")

    args = cast(Arguments, parser.parse_args())

    mdify_achievements(Path(args.path), Path(args.outpath))
