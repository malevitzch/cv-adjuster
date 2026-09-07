from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import cast

from achievements import clean_achievements, mdify_achievements, summarize_achievements


class Arguments(Namespace):
    path: str
    outpath: str
    summary_path: str
    verbose: bool

    def __init__(self) -> None:
        super().__init__()
        self.path = ""
        self.outpath = ""
        self.summary_path = ""
        self.verbose = False


def main() -> None:
    parser = ArgumentParser()
    _ = parser.add_argument("path", help="The path to the source directory")
    _ = parser.add_argument("outpath", help="The path to the output directory")
    _ = parser.add_argument("summary_path", help="The path to the summary file")
    _ = parser.add_argument("-v", "--verbose", action="store_true", help="Print agent logs")

    args = cast(Arguments, parser.parse_args())

    mdify_achievements(Path(args.path), Path(args.outpath))
    summarize_achievements(
        Path(args.outpath), Path(args.summary_path), verbose=args.verbose
    )


def achievements_to_md() -> None:
    parser = ArgumentParser()
    _ = parser.add_argument("path", help="The path to the source directory")
    _ = parser.add_argument("outpath", help="The path to the output directory")
    _ = parser.add_argument("-v", "--verbose", action="store_true", help="Print agent logs")

    args = cast(Arguments, parser.parse_args())
    mdify_achievements(Path(args.path), Path(args.outpath))
    clean_achievements(Path(args.outpath), verbose=args.verbose)


def md_to_summary() -> None:
    parser = ArgumentParser()
    _ = parser.add_argument("path", help="The path to the source directory")
    _ = parser.add_argument("outpath", help="The path to the output directory")
    _ = parser.add_argument("-v", "--verbose", action="store_true", help="Print agent logs")

    args = cast(Arguments, parser.parse_args())
    summarize_achievements(Path(args.path), Path(args.outpath), verbose=args.verbose)
