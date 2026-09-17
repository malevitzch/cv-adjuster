"""Command-line entry point for tailoring a CV to a job offer."""

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import cast

from cv_adjustement import adjust_cv


class Arguments(Namespace):
    raw_path: str
    information_path: str
    offer_path: str
    cv_path: str
    output_path: str
    logs_path: str | None
    verbose: bool


def main() -> None:
    """Run the ``cv-adjust`` command."""
    parser = ArgumentParser(
        description="Create a one-page LaTeX CV tailored to a job offer."
    )
    _ = parser.add_argument(
        "raw_path", help="Directory containing cleaned, Markdown-converted source evidence"
    )
    _ = parser.add_argument(
        "information_path", help="Directory containing achievement summaries"
    )
    _ = parser.add_argument("offer_path", help="Directory containing the job offer")
    _ = parser.add_argument("cv_path", help="Directory containing the current LaTeX CV")
    _ = parser.add_argument("output_path", help="Directory for the tailored CV and PDF")
    _ = parser.add_argument(
        "--logs",
        dest="logs_path",
        help="Directory for evidence and validation logs (default: <output parent>/logs)",
    )
    _ = parser.add_argument("-v", "--verbose", action="store_true", help="Print agent logs")

    args = cast(Arguments, parser.parse_args())
    output_path = Path(args.output_path)
    logs_path = Path(args.logs_path) if args.logs_path else output_path.parent / "logs"
    adjust_cv(
        Path(args.raw_path),
        Path(args.information_path),
        Path(args.offer_path),
        Path(args.cv_path),
        output_path,
        logs_path,
        verbose=args.verbose,
    )
