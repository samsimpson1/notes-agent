from os import mkdir
from os.path import basename, isdir, join
from datetime import datetime
from config import NOTES_PATH

class Log:
    def __init__(self, src_path: str):
        file_name = basename(src_path)
        
        recordings_path = join(NOTES_PATH, "Recordings")
        
        if not isdir(recordings_path):
            mkdir(recordings_path, 0o750)
        
        dest_path = join(recordings_path, f"{file_name}.log")

        self.file = open(dest_path, "w")
    
    def write(self, message: str):
        dt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"[{dt}] {message}"
        print(message)
        self.file.write(message + "\n")
        self.file.flush()
    
    def close(self):
        self.file.close()