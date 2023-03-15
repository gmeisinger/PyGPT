import requests
import json
import os
import openai
from dotenv import load_dotenv
from termcolor import colored, cprint

MODEL_ENGINE = "gpt-3.5-turbo"


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
    conversation_history.append(new_response)
    # Print the response
    # cprint(f"{AI_NAME}: ", AI_COLOR, end=' ')
    # print(f'{message}')
    return conversation_history, message


load_dotenv()

# Set up OpenAI API credentials
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORGANIZATION_ID")
