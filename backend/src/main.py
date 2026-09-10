#!/usr/bin/env python
import sys
import warnings
from dotenv import load_dotenv

from datetime import datetime

from greeting.crew import Greeting

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

load_dotenv(override=True)

def run():
    """
    Run the crew.
    """

    user_name = sys.argv[1] if len(sys.argv) > 1 else 'Guest'
    inputs = {
        'user_name': user_name
    }
    print(f"Running the crew with inputs: {inputs}")

    output = "*** undefined ***"
    try:
        output = Greeting().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
    return output


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        Greeting().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Greeting().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "user_name": "Test User"
    }

    try:
        Greeting().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "user_name": ""
    }

    try:
        result = Greeting().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")

__main__ = __name__ == "__main__"
if __main__:
    run()