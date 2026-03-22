from os import environ
from os.path import join
from datetime import datetime
from base64 import b64encode
from json import loads
from openai import OpenAI
import tools

NOTES_PATH = environ.get("NOTES_PATH", "/home/sam/Documents/Obsidian/Voice")

def invoke(audio_data: bytes, audio_format: str):
    API_KEY = environ.get("GEMINI_API_KEY")

    prompt_path = join(NOTES_PATH, "PROMPT.md")

    prompt = open(prompt_path, 'r').read()

    current_date = datetime.now().strftime("%Y-%m-%d")

    prompt = prompt.replace("DATE_PLACEHOLDER", current_date)

    file = b64encode(audio_data).decode("utf-8")

    openai = OpenAI(
        api_key=API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": [
            {
                "type": "text",
                "text": "Transcribe and record this message."
            },
            {
                "type": "input_audio",
                "input_audio": {
                    "data": file,
                    "format": audio_format
                }
            }
        ]}
    ]

    for i in range(0, 30):
        print(f"iteration {i}")

        response = openai.chat.completions.create(
            model="gemini-3-flash-preview",
            messages=messages,
            tools=tools.TOOLS,
            tool_choice="auto"
        )

        choice = response.choices[0]

        finish_reason = choice.finish_reason
        message = choice.message

        messages.append(choice.message)

        if finish_reason == "stop":
            print("received stop finish_reason")
            return
        
        if finish_reason == "tool_calls":
            for tool_call in message.tool_calls:
                tool_call_id = tool_call.id
                f = tool_call.function

                print(f"tool call: {f.name} with args {f.arguments}")

                func = getattr(tools, f.name)
                args = f.arguments
                tool_call_response = func(**loads(args))

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": tool_call_response
                })