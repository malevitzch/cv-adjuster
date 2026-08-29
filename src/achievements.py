from pathlib import Path

from markitdown import MarkItDown

md = MarkItDown()


def summarize_achievements(source_path: Path, target_path: Path):
    if source_path.is_file():
        result = md.convert(source_path)
        txt = result.markdown
        target_path.parent.mkdir(parents=True, exist_ok=True)
        name = target_path.stem + ".md"
        with open(target_path.with_name(name), "w") as output_file:
            _ = output_file.write(txt)

    elif source_path.is_dir():
        for child in source_path.iterdir():
            summarize_achievements(child, target_path / child.name)
