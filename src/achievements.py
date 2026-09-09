import os
import shutil
from pathlib import Path

from dotenv import load_dotenv
from markitdown import MarkItDown
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

from sandbox import Sandbox, read_only_directory, read_write_directory

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


def summarize_achievements(
    achievements_path: Path, summary_path: Path, verbose: bool = False
) -> None:
    clean_achievements(achievements_path, verbose=verbose)

    summary_path.mkdir(parents=True, exist_ok=True)
    shutil.copytree(achievements_path, summary_path, dirs_exist_ok=True)
    # TODO: have an LLM ingest cleaned achievements and summarize them into a single file at summary_path


def clean_achievements(achievements_path: Path, verbose: bool = False) -> None:
    """Use an isolated coding agent to clean Markdown files in ``achievements_path``."""
    _ = load_dotenv()
    api_key = os.getenv("LLM_API_KEY")
    if api_key is None:
        print("LLM_API_KEY environment variable is not set.")
        return
    base_url = os.getenv("LLM_BASE_URL")
    if base_url is None:
        print("LLM_BASE_URL environment variable is not set.")
        return
    model_name = os.getenv("LLM_MODEL")
    if model_name is None:
        print("LLM_MODEL environment variable is not set.")
        return

    missing = [
        name
        for name, value in (("LLM_API_KEY", api_key), ("LLM_MODEL", model_name))
        if not value
    ]
    if missing:
        raise RuntimeError(
            f"The following environment variables must be set to clean achievements: "
            f"{', '.join(missing)}."
        )

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

        model = OpenAIChatModel(
            model_name,
            provider=OpenAIProvider(base_url=base_url, api_key=api_key),
        )
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
