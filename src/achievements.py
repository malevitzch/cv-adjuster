from datetime import date
from pathlib import Path

from markitdown import MarkItDown
from pydantic_ai import Agent

from models import get_model
from sandbox import Sandbox, read_only_directory, read_write_directory

md = MarkItDown()


def mdify_achievements(source_path: Path, target_path: Path):
    if source_path.is_file():
        result = md.convert(source_path)
        txt = result.markdown
        target_path.parent.mkdir(parents=True, exist_ok=True)
        name = target_path.stem + ".md"
        try:
            with open(target_path.with_name(name), "w") as output_file:
                _ = output_file.write(txt)
        except PermissionError:
            print(f"Permission denied to write {target_path.with_name(name)}")
        except OSError as e:
            print(f"Failed to write file: {e}")

    elif source_path.is_dir():
        for child in source_path.iterdir():
            mdify_achievements(child, target_path / child.name)


def summarize_achievements(
    achievements_path: Path, summary_path: Path, verbose: bool = False
):
    """Summarize cleaned achievements."""
    skill_path = Path(__file__).with_name("skills") / "summarize-achievements.md"
    summarize_skill = skill_path.read_text(encoding="utf-8")

    with Sandbox(
        verbose=verbose,
        directories=[
            read_only_directory("input/"),
            read_write_directory("output/"),
            read_write_directory("logs/"),
        ],
    ) as sandbox:
        sandbox.copy_directory_contents_to(achievements_path, "input/")
        model = get_model()
        agent = Agent(
            model,
            name="achievement-summarizer",
            instructions=(
                "You summarize cleaned Markdown files."
                "Your only workspace access is through the run_command tool, which "
                "runs commands in an isolated environment. Work exclusively on files below "
                "/workspace/output; do not create or modify files elsewhere, including /workspace/input. "
                "Inspect all Markdown files there, apply the following skill, then verify the results. "
                "If there are any uncertainties, report them in the logs.\n\n"
                f"{summarize_skill}"
            ),
        )

        @agent.tool_plain
        def run_command(command: str) -> str:
            """Run an arbitrary shell command in the isolated container workspace."""
            return sandbox.run_command(command)

        prompt = (
            f"Reference date for interpreting relative dates: {date.today().isoformat()}. "
            "Use this date only to interpret things that are relative to the current date. "
            "Be wary of temporal words in old documents, do not automatically assume that "
            "everything is related to today. But in the case of handwritten notes, it is reasonable "
            "to assume that the note was written around the time of the processing, so you can use "
            "the date of the note to interpret relative dates in the note. "
            "Summarize the Markdown files under /workspace/input according to the "
            "summarize-achievements skill, producing summary files in /workspace/output. "
            "Make sure to inspect all input files, and finish only after all files are summarized."
        )

        if verbose:

            async def print_agent_events(_, events) -> None:
                async for event in events:
                    print(event, flush=True)

            agent.run_sync(prompt, event_stream_handler=print_agent_events)
        else:
            agent.run_sync(prompt)

        sandbox.copy_directory_contents_from("output/", summary_path)
        sandbox.copy_directory_contents_from("logs/", "summarize-logs/")


def clean_achievements(achievements_path: Path, verbose: bool = False) -> None:
    """Use an isolated coding agent to clean Markdown files in ``achievements_path``."""
    skill_path = Path(__file__).with_name("skills") / "data-correction.md"
    data_correction_skill = skill_path.read_text(encoding="utf-8")

    with Sandbox(
        verbose=verbose,
        directories=[
            read_only_directory("input/"),
            read_write_directory("output/"),
            read_write_directory("logs/"),
        ],
    ) as sandbox:
        sandbox.copy_directory_contents_to(achievements_path, "input/")
        sandbox.copy_directory_contents_to(achievements_path, "output/")

        model = get_model()
        agent = Agent(
            model,
            name="achievement-cleaner",
            instructions=(
                "You clean Markdown files."
                "Your only workspace access is through the run_command tool, which "
                "runs commands in an isolated environment. Work exclusively on files below "
                "/workspace/output; do not create or modify files elsewhere, including /workspace/input. "
                "Inspect all Markdown files there, apply the following skill, then verify the results. "
                "Remember that the input directory contains a clean copy of the input, which you can use "
                "to assess if any information has been lost, and report that in the logs.\n\n"
                f"{data_correction_skill}"
            ),
        )

        @agent.tool_plain
        def run_command(command: str) -> str:
            """Run an arbitrary shell command in the isolated container workspace."""
            return sandbox.run_command(command)

        prompt = (
            "Clean every Markdown file under /workspace/input according to the "
            "data-correction skill. Edit the files in place, inspect your changes, "
            "and finish only after all files are done."
        )
        if verbose:

            async def print_agent_events(_, events) -> None:
                async for event in events:
                    print(event, flush=True)

            agent.run_sync(prompt, event_stream_handler=print_agent_events)
        else:
            agent.run_sync(prompt)

        sandbox.copy_directory_contents_from("output/", achievements_path)
        sandbox.copy_directory_contents_from("logs/", "mdify-logs/")
