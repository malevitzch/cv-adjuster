from os import sys

from markitdown import MarkItDown


def main():
    args = sys.argv
    md = MarkItDown()
    path = args[1]

    result = md.convert(path)
    print(result.text_content)
