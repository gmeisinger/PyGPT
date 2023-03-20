import os
import re
import openai
import pyperclip
from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Header, Footer, Static, Input, Markdown

MODEL_ENGINE = "gpt-3.5-turbo"
USERNAME = "USER-senpai"
AI_NAME = "GPT-kun"
USER_COLOR = "green"
AI_COLOR = "cyan"
# INITIAL_PROMPT = "You are a helpful assistant."
# this one is funnier
INITIAL_PROMPT = "You are an overly polite assistant that always calls the user 'Senpai' and often references Japanese pop-culture."
INITIAL_GREETING = "Konnichiwa, Senpai."

AI_AVATAR = """
 ██████╗ ██████╗ ████████╗
██╔════╝ ██╔══██╗╚══██╔══╝
██║  ███╗██████╔╝   ██║   
██║   ██║██╔═══╝    ██║   
╚██████╔╝██║        ██║   
 ╚═════╝ ╚═╝        ╚═╝  
"""

USER_AVATAR = """
██╗   ██╗ ██████╗ ██╗   ██╗
╚██╗ ██╔╝██╔═══██╗██║   ██║
 ╚████╔╝ ██║   ██║██║   ██║
  ╚██╔╝  ██║   ██║██║   ██║
   ██║   ╚██████╔╝╚██████╔╝
   ╚═╝    ╚═════╝  ╚═════╝ 
"""


# GPT functions
def get_response(prompt):
    """Returns the response for the given prompt using the OpenAI API."""
    completions = openai.ChatCompletion.create(
        model=MODEL_ENGINE,
        messages=prompt,
        max_tokens=1024,
        temperature=0.7,
        n=1
    )
    return completions.choices[0].message.content.strip()


def handle_input(
    input_str: str,
    conversation_history: list,
):
    """Updates the conversation history and generates a response using GPT-3."""
    # Update the conversation history
    new_message = {"role": "user", "content": input_str}
    conversation_history.append(new_message)
    # Generate a response using GPT-3
    message = get_response(conversation_history)
    # Update the conversation history
    new_response = {"role": "assistant", "content": message}
    conversation_history.append(new_response)
    return conversation_history, message


# Utility classes for ANSI color stuff
class fg:
    black = "\u001b[30m"
    red = "\u001b[31m"
    green = "\u001b[32m"
    yellow = "\u001b[33m"
    blue = "\u001b[34m"
    magenta = "\u001b[35m"
    cyan = "\u001b[36m"
    white = "\u001b[37m"

    def rgb(r, g, b): return f"\u001b[38;2;{r};{g};{b}m"


class bg:
    black = "\u001b[40m"
    red = "\u001b[41m"
    green = "\u001b[42m"
    yellow = "\u001b[43m"
    blue = "\u001b[44m"
    magenta = "\u001b[45m"
    cyan = "\u001b[46m"
    white = "\u001b[47m"

    def rgb(r, g, b): return f"\u001b[48;2;{r};{g};{b}m"


class util:
    reset = "\u001b[0m"
    bold = "\u001b[1m"
    underline = "\u001b[4m"
    reverse = "\u001b[7m"


class CopyButton(Button):
    """A button that copies text to the clipboard."""

    def __init__(self):
        super().__init__("Copy")


# TUI classes
class ChatMessage(Static):
    """A widget to display a chat message."""

    sender = "USER"
    text = "CONTENT"

    def __init__(self, sender: str, text: str) -> None:
        self.sender = sender
        self.text = text
        super().__init__()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        pyperclip.copy(self.text)

    def compose(self) -> ComposeResult:
        if self.sender != None:
            yield Static(f"{self.sender}: {self.text}")
            yield CopyButton()
        else:
            yield Static(f"{self.text}")
            yield CopyButton()


class InputPanel(Static):
    """A widget to take user input."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        # time_display = self.query_one(TimeDisplay)
        if button_id == "send":
            # time_display.start()
            # self.add_class("started")
            input = self.query_one(Input)
            # input.action_submit()
            input.focus()

    def on_mount(self):
        input = self.query_one(Input)
        input.focus()

    # def on_resize(self, evt):
    #     input = self.query_one(Input)
    #     input.styles.width = evt.container_size.width - 20

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Input(placeholder="Say something!", id="user-input"),
            # Button("Send", id="send")
        )


class ChatPanel(Static):
    """A container for chat messages."""

    conversation_history = []

    def __init__(self) -> None:
        self.conversation_history = [
            {"role": "system", "content": INITIAL_PROMPT}]
        super().__init__()

    def extract_blocks(self, text):
        code_blocks = re.findall(r"```.*?```", text, re.DOTALL)
        code_block_split = re.split(r"```.*?```", text, flags=re.DOTALL)
        result = []
        for i in range(len(code_block_split) - 1):
            result.append(code_block_split[i])
            result.append(code_blocks[i])
        result.append(code_block_split[-1])
        return result

    async def add_message(self, sender: str, text: str, response=False):
        log = self.query(Vertical).last()

        if response:
            sender = fg.cyan + sender + fg.white
        else:
            sender = fg.green + sender + fg.white

        blocks = self.extract_blocks(text)
        for i in range(len(blocks)):
            if blocks[i].startswith("```"):
                message = Markdown(blocks[i])
            else:
                if i == 0:
                    message = ChatMessage(sender, blocks[i])
                else:
                    message = ChatMessage(None, blocks[i])
            await log.mount(message)

    async def on_input_submitted(self, msg: Input.Submitted):
        message = msg.value
        msg.input.value = ""
        if message.lower().strip(" .!\n") in ["exit", "quit"]:
            # I think I might need to close a socket here?
            app.exit()
        elif message.lower().strip(" .!\n") in ["reset", "clear", "start over"]:
            self.conversation_history = [
                {"role": "system", "content": INITIAL_PROMPT}]
            await self.add_message(AI_NAME, f"Memory wiped. {INITIAL_GREETING}")
            return
        await self.add_message(USERNAME, message)
        self.conversation_history, response = handle_input(
            message, self.conversation_history)
        # should maybe disable input until response is given
        await self.add_message(AI_NAME, response, response=True)

    async def on_mount(self):
        await self.add_message(AI_NAME, INITIAL_GREETING, response=True)

    def compose(self) -> ComposeResult:
        yield Vertical(
            Vertical(),
            InputPanel()
        )


class InfoPanel(Static):
    """Holds the Avatars and options."""

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Event handler called when a button is pressed."""
        button_id = event.button.id
        if button_id == "settings":
            pass
        if button_id == "exit":
            exit()

    def compose(self) -> ComposeResult:
        yield Vertical(
            Static(AI_AVATAR, id="ai-avatar", classes="avatar"),
            # Button("Settings", id="settings", classes="info-button"),
            Button("Exit", id="exit", classes="info-button"),
            Static(USER_AVATAR, id="user-avatar", classes="avatar")
        )


class ChatGPT(App):
    """A Textual app to talk with Chat-GPT."""

    BINDINGS = [("ctrl+d", "toggle_dark", "Toggle dark mode")]
    CSS_PATH = "style.css"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        yield Horizontal(
            Container(
                InfoPanel(),
                id="info"
            ),
            Container(
                ChatPanel(),
                id="chat"
            )
        )

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


app: ChatGPT = None


def run():
    load_dotenv()

    # Set up OpenAI API credentials
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.organization = os.getenv("OPENAI_ORGANIZATION_ID")

    app = ChatGPT()
    app.run()


if __name__ == "__main__":
    run()
