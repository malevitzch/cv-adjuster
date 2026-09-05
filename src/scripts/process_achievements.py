from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import cast

from achievements import mdify_achievements, summarize_achievements


class Arguments(Namespace):
    path: str
    outpath: str
    summary_path: str

    def __init__(self) -> None:
        super().__init__()
        self.path = ""
        self.outpath = ""
        self.summary_path = ""


# TODO: this should be decoupled into mdification and sumarization commands
# and maybe one deluxe script that does both
def main() -> None:
    parser = ArgumentParser()
    _ = parser.add_argument("path", help="The path to the source directory")
    _ = parser.add_argument("outpath", help="The path to the output directory")
    _ = parser.add_argument("summary_path", help="The path to the summary file")

    args = cast(Arguments, parser.parse_args())

    mdify_achievements(Path(args.path), Path(args.outpath))
    summarize_achievements(Path(args.outpath), Path(args.summary_path))
