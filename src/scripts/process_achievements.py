import sys
from pathlib import Path

from achievements import summarize_achievements


def main():
    args = sys.argv
    path = args[1]
    outpath = args[2]

    summarize_achievements(Path(path), Path(outpath))
