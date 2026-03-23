from argparse import ArgumentParser
from os import mkdir
from os.path import basename, splitext, isdir, join
from shutil import copyfile
from llm import invoke
from log import Log
from config import NOTES_PATH


def copy_recording(src_path: str):
    file_name = basename(src_path)
    
    recordings_path = join(NOTES_PATH, "Recordings")
    
    if not isdir(recordings_path):
        mkdir(recordings_path, 0o750)
    
    dest_path = join(recordings_path, file_name)
    copyfile(src_path, dest_path)

def main():
    parser = ArgumentParser()
    parser.add_argument("audio_file", help="Path to the audio file")
    args = parser.parse_args()
    
    file_name = basename(args.audio_file)
    _, ext = splitext(file_name)
    ext = ext[1:]

    with open(args.audio_file, "rb") as f:
        audio_data = f.read()
    
    copy_recording(args.audio_file)
    
    log = Log(args.audio_file)
    
    invoke(audio_data, ext, log)

    log.close()

if __name__ == "__main__":
    main()
