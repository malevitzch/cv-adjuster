"""Tailor a LaTeX CV to a job offer in an isolated agent sandbox."""

from pathlib import Path

from pydantic_ai import Agent

from models import get_model
from sandbox import (
    DEFAULT_DOCKERFILE_DIR,
    Sandbox,
    read_only_directory,
    read_write_directory,
)


LATEX_DOCKERFILE = DEFAULT_DOCKERFILE_DIR / "Dockerfile.latex.sandbox"


def adjust_cv(
    raw_path: Path,
    information_path: Path,
    offer_path: Path,
    cv_path: Path,
    output_path: Path,
    logs_path: Path,
    *,
    verbose: bool = False,
) -> None:
    """Create a one-page, job-tailored CV from the supplied directories.

    Input directories are mounted in the sandbox as read-only copies.  The
    agent may write only its CV deliverables and validation logs, which are
    copied back to ``output_path`` and ``logs_path`` respectively.
    """
    _validate_input_directories(raw_path, information_path, offer_path, cv_path)

    skill_path = Path(__file__).with_name("skills") / "cv-adjustement.md"
    cv_adjustment_skill = skill_path.read_text(encoding="utf-8")

    with Sandbox(
        tag="cv-adjuster-latex:latest",
        name="cv_adjuster_container",
        verbose=verbose,
        dockerfile=LATEX_DOCKERFILE,
        directories=[
            read_only_directory("raw/"),
            read_only_directory("information/"),
            read_only_directory("offer/"),
            read_only_directory("cv/"),
            read_write_directory("output/"),
            read_write_directory("logs/"),
        ],
    ) as sandbox:
        sandbox.copy_directory_contents_to(raw_path, "raw/")
        sandbox.copy_directory_contents_to(information_path, "information/")
        sandbox.copy_directory_contents_to(offer_path, "offer/")
        sandbox.copy_directory_contents_to(cv_path, "cv/")

        agent = Agent(
            get_model(),
            name="cv-adjuster",
            instructions=(
                "You tailor LaTeX CVs to job offers. Your only workspace access is "
                "through the run_command tool, which runs commands in an isolated "
                "environment. Work exclusively below /workspace/output and "
                "/workspace/logs; never modify /workspace/raw, /workspace/information, "
                "/workspace/offer, or /workspace/cv. Read the job offer and source "
                "materials, apply the following skill, then verify the final files.\n\n"
                f"{cv_adjustment_skill}"
            ),
        )

        @agent.tool_plain
        def run_command(command: str) -> str:
            """Run a shell command in the isolated CV workspace."""
            return sandbox.run_command(command)

        prompt = (
            "Create a tailored CV according to the cv-adjustement skill. Inspect every "
            "file in /workspace/offer, use the existing LaTeX CV in /workspace/cv as "
            "the template, and use /workspace/information as the primary evidence source. "
            "Use /workspace/raw only when necessary to resolve ambiguous or missing "
            "support. Write deliverables to /workspace/output and unresolved evidence "
            "or validation issues to /workspace/logs. Do not finish until you have "
            "performed the compilation and one-page checks required by the skill."
        )
        if verbose:

            async def print_agent_events(_, events) -> None:
                async for event in events:
                    print(event, flush=True)

            agent.run_sync(prompt, event_stream_handler=print_agent_events)
        else:
            agent.run_sync(prompt)

        sandbox.copy_directory_contents_from("output/", output_path)
        sandbox.copy_directory_contents_from("logs/", logs_path)


def _validate_input_directories(*paths: Path) -> None:
    for path in paths:
        if not path.is_dir():
            raise NotADirectoryError(path)

