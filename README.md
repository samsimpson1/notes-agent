# notes-agent

An agent to transcribe voice notes into markdown.

System prompt is read from `$NOTES_PATH/PROMPT.md`. The agent cannot write to this path.

## Config

* `GEMINI_API_KEY` - API key for Gemini.
* `NOTES_PATH` - path to Obsidian notes directory. All file operations are relative to this path.
* `MAX_ITERATIONS` - maximum number of LLM iterations for a given voice message. Default: 30