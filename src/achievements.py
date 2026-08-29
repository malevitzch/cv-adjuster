import os
from pathlib import Path

from dotenv import load_dotenv
from markitdown import MarkItDown

md = MarkItDown()


def mdify_achievements(source_path: Path, target_path: Path):
    if source_path.is_file():
        result = md.convert(source_path)
        txt = result.markdown
        target_path.parent.mkdir(parents=True, exist_ok=True)
        name = target_path.stem + ".md"
        with open(target_path.with_name(name), "w") as output_file:
            # TODO: check if it didn't fail, maybe log somewhere
            _ = output_file.write(txt)

    elif source_path.is_dir():
        for child in source_path.iterdir():
            mdify_achievements(child, target_path / child.name)


def clean_achievements():
    _ = load_dotenv()

    openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
