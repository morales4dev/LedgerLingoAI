from styles import CSS, JS, EXAMPLES
from dotenv import load_dotenv
import gradio as gr
from context import get_absolute_path
from greeting.crew import Greeting

load_dotenv(override=True)


def chat(message, history):
    """
    Run the crew.
    """

    user_name = message if len(message) > 1 else 'Guest'
    inputs = {
        'user_name': user_name
    }
    print(f"Running the crew with inputs: {inputs}")

    output = "*** undefined ***"
    try:
        output = Greeting().crew().kickoff(inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")
    return output.raw


if __name__ == "__main__":
    gr.ChatInterface(
        chat,
        examples=EXAMPLES,
        title="Personal Welcome Concierge",
        description="Dime tu nombre y yo te saludo",
        chatbot=gr.Chatbot(show_label=False),
    ).launch(css=CSS, js=JS, theme=gr.themes.Base())
