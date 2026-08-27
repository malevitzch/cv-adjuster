from pathlib import Path


def convert(filepath: Path):
    if not filepath.exists():
        raise FileNotFoundError(f"No such file as {filepath}")
    # TODO: actually do the conversion
