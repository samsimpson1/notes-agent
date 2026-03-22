from os.path import join
from datetime import datetime
from base64 import b64encode
from json import loads
from openai import OpenAI
import tools
from log import Log
from config import NOTES_PATH, API_KEY, API_BASE_URL, MODEL, MAX_ITERATIONS


def invoke(audio_data: bytes, audio_format: str, log: Log):
    prompt_path = join(NOTES_PATH, "PROMPT.md")

    prompt = open(prompt_path, 'r').read()

    current_date = datetime.now().strftime("%Y-%m-%d")

    prompt = prompt.replace("DATE_PLACEHOLDER", current_date)

    file = b64encode(audio_data).decode("utf-8")

    openai = OpenAI(
        api_key=API_KEY,
        base_url=API_BASE_URL
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

    for i in range(0, MAX_ITERATIONS):
        print(f"iteration {i}")
        log.write(f"Iteration {i}/{MAX_ITERATIONS}")

        response = openai.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools.TOOLS,
            tool_choice="auto"
        )

        choice = response.choices[0]

        finish_reason = choice.finish_reason
        message = choice.message

        messages.append(choice.message)

        if finish_reason == "stop":
            log.write("Received stop finish_reason")
            return
        
        if finish_reason == "tool_calls":
            for tool_call in message.tool_calls:
                tool_call_id = tool_call.id
                f = tool_call.function

                log.write(f"Tool call: {f.name} with args {f.arguments}")

                func = getattr(tools, f.name)
                args = f.arguments
                tool_call_response = func(**loads(args))

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": tool_call_response
                })