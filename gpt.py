import requests
import json
import os
import openai
from dotenv import load_dotenv
from termcolor import colored, cprint

MODEL_ENGINE = "gpt-3.5-turbo"
USERNAME = "USER"
AI_NAME = "ChatGPT"
USER_COLOR = "green"
AI_COLOR = "cyan"
# INITIAL_PROMPT = "You are a helpful assistant."
# this one is funnier
INITIAL_PROMPT = "You are an overly polite assistant that always calls the user 'Master'."
INITIAL_GREETING = "Hello, Master."


def get_response(prompt):
    """Returns the response for the given prompt using the OpenAI API."""
    completions = openai.ChatCompletion.create(
        model=MODEL_ENGINE,
        messages=prompt,
        max_tokens=1024,
        temperature=0.7,
    )
    return completions.choices[0].message.content.strip()


def handle_input(
    input_str: str,
    conversation_history: list,
    USERNAME: str,
    AI_NAME: str,
):
    """Updates the conversation history and generates a response using GPT-3."""
    # Update the conversation history
    new_message = {"role": "user", "content": input_str}
    conversation_history.append(new_message)
    # conversation_history += f"{USERNAME}: {input_str}\n"
    # Generate a response using GPT-3
    message = get_response(conversation_history)
    # Update the conversation history
    new_response = {"role": "assistant", "content": message}
    # Print the response
    cprint(f"{AI_NAME}: ", AI_COLOR, end=' ')
    print(f'{message}')
    return conversation_history


load_dotenv()

# Set up OpenAI API credentials
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORGANIZATION_ID")

# Set the initial prompt to include a personality and habits
conversation_history = [{"role": "system", "content": INITIAL_PROMPT}]

cprint(f"{AI_NAME}: ", AI_COLOR, end=' ')
print(f"{INITIAL_GREETING}")

# start the loop
while True:
    # Get the user's input
    cprint(f"{USERNAME}: ", USER_COLOR, end=' ')
    user_input = input()

    if user_input.lower() in ["exit", "quit"]:
        exit()
    elif user_input.lower() in ["reset", "clear", "start over"]:
        conversation_history = [{"role": "system", "content": INITIAL_PROMPT}]
        cprint(f"{AI_NAME}: ", AI_COLOR, end=' ')
        print(f"Memory wiped. {INITIAL_GREETING}")
        # print(f"{AI_NAME}: Memory wiped. {INITIAL_GREETING}")
    else:
        # Handle the input
        conversation_history = handle_input(
            user_input, conversation_history, USERNAME, AI_NAME)
