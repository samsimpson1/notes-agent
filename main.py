from llm import invoke


def main():
    with open("test.mp3", "rb") as f:
        audio_data = f.read()

    invoke(audio_data, "mp3")

if __name__ == "__main__":
    main()
