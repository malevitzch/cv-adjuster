from collections.abc import Callable
from pathlib import Path


def validate_ext(extensions: list[str]):
    def decorator(func: Callable[[Path], bool]):
        def adapter(path: Path):
            if path.suffix in extensions:
                return func(path)
            else:
                return False

        return adapter

    return decorator


def ext_check(extensions: list[str] | str):
    def adapter(path: Path):
        if isinstance(extensions, str):
            return path.suffix == extensions
        else:
            return path.suffix in extensions

    return adapter
