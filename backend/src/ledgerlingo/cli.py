import argparse
import asyncio
from collections.abc import Sequence

from ledgerlingo.agent import AgentError
from ledgerlingo.client import create_client
from ledgerlingo.config import SettingsError, load_settings
from ledgerlingo.orchestrator import process_question


async def _run_question(question: str) -> str:
    settings = load_settings()
    async with create_client(settings) as client:
        return await process_question(question, settings, client)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ask LedgerLingo a question.")
    parser.add_argument("question", help="Question to send to the agent.")
    args = parser.parse_args(argv)

    try:
        answer = asyncio.run(_run_question(args.question))
    except (AgentError, SettingsError) as error:
        parser.exit(status=1, message=f"ledgerlingo: error: {error}\n")

    print(answer)
    return 0
