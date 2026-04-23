from argparse import ArgumentParser
from os import mkdir
from os.path import basename, splitext, isdir, join, isfile
from shutil import copyfile
from sys import exit
from llm import invoke
from log import Log
from config import NOTES_PATH


def copy_recording(src_path: str, overwrite: bool = False):
    file_name = basename(src_path)
    
    recordings_path = join(NOTES_PATH, "Recordings")
    
    if not isdir(recordings_path):
        mkdir(recordings_path, 0o750)
    
    dest_path = join(recordings_path, file_name)

    if isfile(dest_path) and not overwrite:
        print(f"Recording {file_name} has already been processed.")
        print("Use --overwrite to process again.")
        exit(0)

    copyfile(src_path, dest_path)

def main():
    parser = ArgumentParser()
    parser.add_argument("audio_file", help="Path to the audio file")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing audio file instead of skipping")
    args = parser.parse_args()
    
    file_name = basename(args.audio_file)
    _, ext = splitext(file_name)
    ext = ext[1:]

    copy_recording(args.audio_file, args.overwrite)

    log = Log(args.audio_file)

    invoke(args.audio_file, ext, log)

    log.close()

if __name__ == "__main__":
    main()
