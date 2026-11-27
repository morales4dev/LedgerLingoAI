import argparse
import asyncio
from collections.abc import Sequence
import sys
import traceback

from ledgerlingo.agent import AgentError, interpret_query
from ledgerlingo.config import SettingsError, load_settings
from ledgerlingo.dimension_lookup import DimensionLookupError
from ledgerlingo.models import QueryInterpretation
from ledgerlingo.orchestrator import process_question


async def _run_question(question: str, debug: bool = False) -> str:
    settings = load_settings()
    return await process_question(question, settings, debug=debug)


async def _run_interpretation(question: str) -> QueryInterpretation:
    settings = load_settings()
    return await interpret_query(question, settings)


def _exit_with_error(
    parser: argparse.ArgumentParser,
    error: Exception,
    debug: bool,
) -> None:
    if debug:
        traceback.print_exception(error)
        parser.exit(status=1)
    parser.exit(status=1, message=f"ledgerlingo: error: {error}\n")


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(argv) if argv is not None else sys.argv[1:]
    if arguments and arguments[0] == "interpret":
        parser = argparse.ArgumentParser(
            prog="ledgerlingo interpret",
            description="Inspect a natural-language interpretation as JSON.",
        )
        parser.add_argument(
            "question",
            help="Question to interpret without validation or calculation.",
        )
        parser.add_argument(
            "--debug",
            action="store_true",
            help="Print the full exception traceback if interpretation fails.",
        )
        args = parser.parse_args(arguments[1:])
        try:
            interpretation = asyncio.run(_run_interpretation(args.question))
        except (AgentError, DimensionLookupError, SettingsError) as error:
            _exit_with_error(parser, error, args.debug)
        print(interpretation.model_dump_json(indent=2))
        return 0

    parser = argparse.ArgumentParser(description="Ask LedgerLingo a question.")
    parser.add_argument("question", help="Question to send to the agent.")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print the full exception traceback if processing fails.",
    )
    args = parser.parse_args(arguments)

    try:
        answer = asyncio.run(_run_question(args.question, debug=args.debug))
    except (AgentError, SettingsError) as error:
        _exit_with_error(parser, error, args.debug)

    print(answer)
    return 0
