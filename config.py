from os import environ

NOTES_PATH = environ.get("NOTES_PATH", "/home/sam/Documents/Obsidian/Voice")
API_KEY = environ.get("API_KEY")
MODEL = environ.get("MODEL", "gemini-3-flash-preview")
MAX_ITERATIONS = int(environ.get("MAX_ITERATIONS", "30"))