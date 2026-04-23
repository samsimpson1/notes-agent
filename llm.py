from os.path import join
from datetime import datetime
from google import genai
from google.genai import types
import tools
from log import Log
from config import NOTES_PATH, API_KEY, MODEL, MAX_ITERATIONS


def invoke(audio_path: str, audio_format: str, log: Log):
    prompt_path = join(NOTES_PATH, "PROMPT.md")

    prompt = open(prompt_path, 'r').read()

    current_date = datetime.now().strftime("%Y-%m-%d")

    prompt = prompt.replace("DATE_PLACEHOLDER", current_date)

    client = genai.Client(api_key=API_KEY)

    log.write(f"Uploading audio via Files API: {audio_path}")
    audio_file = client.files.upload(
        file=audio_path,
        config=types.UploadFileConfig(mime_type=f"audio/{audio_format}"),
    )
    log.write(f"Uploaded file: {audio_file.name}")

    try:
        contents = [
            types.Content(role="user", parts=[
                types.Part.from_text(text="Transcribe and record this message."),
                types.Part.from_uri(file_uri=audio_file.uri, mime_type=audio_file.mime_type),
            ]),
        ]

        config = types.GenerateContentConfig(
            system_instruction=prompt,
            tools=tools.TOOLS,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        )

        for i in range(0, MAX_ITERATIONS):
            log.write(f"Iteration {i}/{MAX_ITERATIONS}")

            response = client.models.generate_content(
                model=MODEL,
                contents=contents,
                config=config,
            )

            candidate = response.candidates[0]
            contents.append(candidate.content)

            function_calls = [p.function_call for p in candidate.content.parts if p.function_call]

            if not function_calls:
                log.write("Received stop finish_reason")
                return

            tool_response_parts = []
            for fc in function_calls:
                log.write(f"Tool call: {fc.name} with args {fc.args}")

                func = getattr(tools, fc.name)
                result = func(**(fc.args or {}))

                tool_response_parts.append(
                    types.Part.from_function_response(name=fc.name, response={"result": result})
                )

            contents.append(types.Content(role="user", parts=tool_response_parts))
    finally:
        try:
            client.files.delete(name=audio_file.name)
            log.write(f"Deleted uploaded file: {audio_file.name}")
        except Exception as e:
            log.write(f"Failed to delete uploaded file {audio_file.name}: {e}")
