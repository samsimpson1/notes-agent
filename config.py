from os import environ

NOTES_PATH = environ.get("NOTES_PATH", "/home/sam/Documents/Obsidian/Voice")
API_KEY = environ.get("API_KEY")
API_BASE_URL = environ.get("API_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
MODEL = environ.get("MODEL", "gemini-3-flash-preview")
MAX_ITERATIONS = int(environ.get("MAX_ITERATIONS", "30"))