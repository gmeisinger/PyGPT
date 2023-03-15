from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Header, Footer, Static, Input, Placeholder, TextLog, Label
from src import gpt


USERNAME = "USER-senpai"
AI_NAME = "GPT-kun"
USER_COLOR = "green"
AI_COLOR = "cyan"
# INITIAL_PROMPT = "You are a helpful assistant."
# this one is funnier
INITIAL_PROMPT = "You are an overly polite assistant that always calls the user 'Senpai' and often references Japanese pop-culture."
INITIAL_GREETING = "Konnichiwa, Senpai."


class Avatar(Static):
    """A widget to display an ascii-art avatar."""


class ChatMessage(Static):
    """A widget to display a chat message."""

    sender = "USER"
    text = "CONTENT"

    def __init__(self, sender: str, text: str) -> None:
        self.sender = sender
        self.text = text
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Static(f"{self.sender}: {self.text}")


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

    def compose(self) -> ComposeResult:
        yield Container(
            Input(placeholder="Say something!"),
            Button("Send", id="send")
        )


class ChatPanel(Static):
    """A container for chat messages."""

    size = None
    conversation_history = []

    def __init__(self, size) -> None:
        self.size = size
        self.conversation_history = [
            {"role": "system", "content": INITIAL_PROMPT}]
        super().__init__()

    async def add_message(self, sender: str, text: str, response=False):
        log = self.query(Vertical).last()
        message = ChatMessage(sender, text)
        await log.mount(message)

    async def on_input_submitted(self, msg: Input.Submitted):
        if msg.value in ["exit", "quit"]:
            exit()
        await self.add_message("USER", msg.value)
        msg.input.value = ""
        self.conversation_history, message = gpt.handle_input(
            msg.value, self.conversation_history, USERNAME, AI_NAME)
        self.add_message("system", str(self.conversation_history))
        # should maybe disable input until response is given
        self.add_message(AI_NAME, message, response=True)

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
        # time_display = self.query_one(TimeDisplay)
        if button_id == "settings":
            pass
        if button_id == "exit":
            exit()

    def compose(self) -> ComposeResult:
        yield Vertical(
            Placeholder(id="ai-avatar", classes="avatar"),
            Button("Settings", id="settings", classes="info-button"),
            Button("Exit", id="exit", classes="info-button"),
            Placeholder(id="user-avatar", classes="avatar")
        )


class ChatApp(App):
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
                ChatPanel(self.size),
                id="chat"
            )
        )

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark


def run():
    app = ChatApp()
    app.run()


if __name__ == "__main__":
    run()
