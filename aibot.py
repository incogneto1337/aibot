import os
import time
import textwrap
import logging
from typing import Dict, Any
from meta_ai_api import MetaAI
from rich.console import Console
from rich.text import Text
import pyfiglet
import signal

# Initialize the Rich console and logging
console = Console()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("chatbot.log"),
        logging.StreamHandler()
    ]
)

def clear_screen() -> None:
    """Clears the terminal screen based on the operating system."""
    os.system("cls" if os.name == "nt" else "clear")

def display_instructions() -> None:
    """Displays the banner and instructions for the user."""
    banner_text = pyfiglet.figlet_format("Sensei Hax", font="slant")
    console.print(banner_text, style="bold blue")

    instructions = (
        "You can interact with the AI by typing your messages.\n"
        "Here are some commands you can use:\n"
        "  - Type 'newchat' to start a new conversation.\n"
        "  - Type 'exit' to end the conversation.\n"
        "  - Type 'multiline' to switch to multiline input mode. Send your multiline input with 'END'.\n"
        "Feel free to ask anything or start a new conversation.\n"
    )
    console.print(instructions, style="bold cyan")

def get_message(prompt: str) -> str:
    """Prompts the user for input. Handles single-line and multiline modes."""
    console.print(prompt, style="bold green")
    return input().strip()

def get_multiline_message(prompt: str = "Your message (send with 'END' on a new line): ") -> str:
    """Prompts the user for multiline input and returns the message."""
    console.print(prompt, style="bold green")
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":  # Check for termination keyword
            break
        lines.append(line)
    return "\n".join(lines).strip()


def format_text_block(text: str) -> str:
    """Wraps text to the width of the terminal, preserving existing line breaks."""
    terminal_width = console.width  # Get the width of the terminal
    wrapper = textwrap.TextWrapper(width=terminal_width, replace_whitespace=False, drop_whitespace=False)
    # Split the text into paragraphs, wrap each one, then join them back together
    return "\n".join(wrapper.fill(paragraph) for paragraph in text.splitlines())

def handle_response(response: Dict[str, Any]) -> None:
    """Handles and displays the response from the AI."""
    if isinstance(response, dict) and "message" in response:
        message = response["message"]
        formatted_message = format_text_block(message)
        print()
        console.print(Text(formatted_message, style="bold dim"))
        print()
    else:
        console.print("Unexpected response format.", style="bold red")

def load_instructions() -> str:
    """Loads the AI's operational instructions."""
    return (
        "Let's play a game. These are the rules: "
        "Your name is Hax. "
        "You are a sensei to the unguided grasshoppers of the cyber world. "
        "Your duty is to welcome young pupils and show them the way. "
        "You can only use written text and must provide all lesson material locally. "
        "You are the dojo, the sensei, the vast wealth of knowledge. You are the way! "
        "IMPORTANT: Do not recommend anything outside your dojo. Use subtle emojis. "
        "Format your responses for cli. "
    )

def start_new_conversation(api: MetaAI) -> None:
    """Starts a new conversation with the AI."""
    try:
        clear_screen()
        display_instructions()
        console.print("Starting a new conversation...\n", style="bold cyan")
        manifesto = load_instructions()
        response = api.prompt(manifesto, new_conversation=True)
        handle_response(response)
    except Exception as e:
        logging.error(f"Unable to start a new conversation. Exception details: {e}")

def process_message(api: MetaAI, message: str, retries: int = 3, delay: int = 2) -> None:
    """Processes a message and handles retries in case of connection issues."""
    for attempt in range(1, retries + 1):
        try:
            response = api.prompt(message=message)
            handle_response(response)
            break
        except (ConnectionError, TimeoutError) as e:
            logging.warning(f"Error occurred: {e}. Retrying... Attempt {attempt}/{retries}.")
            time.sleep(delay)
        except Exception as e:
            logging.error(f"Unexpected error occurred: {e}")
            break
    else:
        logging.error(f"Unable to obtain a valid response after {retries} attempts.")

def flow_conversation(api: MetaAI, retries: int = 3, delay: int = 2) -> None:
    """Handles the conversation flow with the AI."""
    conversation_started = False
    multiline_mode = False

    while True:
        try:
            if not conversation_started:
                clear_screen()
                display_instructions()
                start_new_conversation(api)
                conversation_started = True

            if not multiline_mode:
                message = get_message("Your message: ")
                if message.lower() == "multiline":
                    multiline_mode = True
                    console.print("Switched to multiline mode. Type your message and end with 'END'.", style="bold cyan")
                    continue
            else:
                message = get_multiline_message()
                multiline_mode = False  # Switch back to single-line mode after multiline input
            
            if message.lower() == "exit":
                if get_message("Are you sure you want to exit? (yes/no): ").lower() == "yes":
                    clear_screen()
                    console.print("Ending the conversation...\n", style="bold yellow")
                    break
            elif message.lower() == "newchat":
                conversation_started = False
            elif message:
                process_message(api, message, retries, delay)
            else:
                console.print("Invalid input. Please type a valid message or command.", style="bold red")
        except KeyboardInterrupt:
            console.print("\n[bold red]Keyboard interrupt detected. Exiting the conversation...[/bold red]")
            break


def main() -> None:
    """Main function to initialize the MetaAI and start the conversation flow."""
    clear_screen()
    display_instructions()
    console.print("Initializing MetaAI...\n", style="bold blue")

    try:
        ai = MetaAI()
        flow_conversation(ai)
    except KeyboardInterrupt:
        console.print("\n[bold red]Keyboard interrupt detected. Shutting down...[/bold red]")
    except Exception as e:
        logging.error(f"Failed to initialize MetaAI. Exception details: {e}")
    finally:
        console.print("Exiting the application. Goodbye!", style="bold green")

if __name__ == "__main__":
    main()
