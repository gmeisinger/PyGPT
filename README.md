# Terminal Based Chat-GPT

## Install

```
pip install openai python-dotenv termcolor
```

Edit `.env` to use your api key and organization id (found [here](https://platform.openai.com/account/org-settings))

```
python ./gpt.py
```

## Use

Just type in your prompt. The request is sent to the `text-davinci-003` model for text completion.

To quit, type `exit` or `quit`.

Reset the conversation with `reset`, `clear` or `start over`

All other text is considered a prompt and sent to GPT.