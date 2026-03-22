import subprocess
from os import mkdir
from os.path import join, getmtime
from config import NOTES_PATH

TOOLS = [
  {
    "type": "function",
    "function": {
      "name": "create_directory",
      "description": "Create a directory at the given path",
      "parameters": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string",
            "description": "Absolute path of directory to create"
          }
        },
        "required": ["path"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "read_file",
      "description": "Read a .md file from the notes directory, returning its contents",
      "parameters": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string",
            "description": 'Path to the file, starting with "/"'
          },
          "offset": {
            "type": "integer",
            "description": "Number of lines to skip from the beginning of the file (default: 0)"
          },
          "limit": {
            "type": "integer",
            "description": "Maximum number of lines to return (default: 2000)"
          }
        },
        "required": ["path"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "edit_file",
      "description": "Perform an exact string replacement in a .md file",
      "parameters": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string",
            "description": 'Path to the file, starting with "/"'
          },
          "old_string": {
            "type": "string",
            "description": "The exact string to search for and replace. Must appear exactly once unless replace_all is true."
          },
          "new_string": {
            "type": "string",
            "description": "The string to replace old_string with"
          },
          "replace_all": {
            "type": "boolean",
            "description": "If true, replace all occurrences of old_string; if false (default), errors when old_string appears more than once"
          }
        },
        "required": ["path", "old_string", "new_string"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "write_file",
      "description": "Write content to a .md file, creating it if it doesn't exist or overwriting it",
      "parameters": {
        "type": "object",
        "properties": {
          "path": {
            "type": "string",
            "description": 'Path to the file, starting with "/"'
          },
          "content": {
            "type": "string",
            "description": "Full content to write to the file"
          }
        },
        "required": ["path", "content"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "glob_files",
      "description": "Find files matching a glob pattern within a directory",
      "parameters": {
        "type": "object",
        "properties": {
          "pattern": {
            "type": "string",
            "description": "Glob pattern to match files"
          },
          "path": {
            "type": "string",
            "description": 'Directory to search in, starting with "/" (default: "/")'
          }
        },
        "required": ["pattern"]
      }
    }
  },
  {
    "type": "function",
    "function": {
      "name": "grep_files",
      "description": "Search for a regex pattern within files using ripgrep",
      "parameters": {
        "type": "object",
        "properties": {
          "pattern": {
            "type": "string",
            "description": "Regex pattern to search for"
          },
          "path": {
            "type": "string",
            "description": 'Directory or file to search in, starting with "/" (default: "/")'
          },
          "glob": {
            "type": "string",
            "description": 'Glob pattern to filter which files are searched (e.g. "*.md")'
          },
          "output_mode": {
            "type": "string",
            "description": 'Output format: "files_with_matches" (default) returns one path per file with a match; "content" returns matching lines with line numbers in "<path>:<line>:<text>" format; "count" returns one "<path>:<n>" per file with match count'
          },
          "case_insensitive": {
            "type": "boolean",
            "description": "If true, match regardless of case (default: false)"
          },
          "context": {
            "type": "integer",
            "description": "Number of lines to show before and after each match, content mode only (default: 0)"
          },
          "multiline": {
            "type": "boolean",
            "description": "If true, allow patterns to span multiple lines (default: false)"
          }
        },
        "required": ["pattern"]
      }
    }
  }
]

PROTECTED_PATHS = [
  "/PROMPT.md"
]

def create_directory(path: str) -> str:
  """Create a directory at the given path."""

  if ".." in path:
    return "ERROR: .. not permitted in path"
  
  if not path.startswith("/"):
    return "ERROR: path must start with /"
  
  path = path[1:]
  
  abs_dir_path = join(NOTES_PATH, path)

  try:
    mkdir(abs_dir_path, 0o750)
  except FileExistsError:
    return "OK"
  except FileNotFoundError:
    return "ERROR: Parent directory does not exist"
  except:
    return "ERROR: Unknown error occurred"

  return "OK"

def read_file(path: str, offset: int = 0, limit: int = 2000) -> str:
  """Read a .md file from the notes directory, returning its contents with line numbers.

  Args:
    path: Path to the file, starting with "/".
    offset: Number of lines to skip from the beginning of the file (default: 0).
    limit: Maximum number of lines to return (default: 2000).

  Returns lines in cat -n format: each line is prefixed with its 1-based line number
  (right-justified, width 6) followed by a tab character.
  """
  if ".." in path:
    return "ERROR: .. not permitted in path"
  
  if not path.endswith(".md"):
    return "ERROR: path must end in .md"
  
  if not path.startswith("/"):
    return "ERROR: path must start with /"
  
  path = path[1:]
  
  abs_file_path = join(NOTES_PATH, path)

  try:
    with open(abs_file_path, 'r') as f:
      line_num = 0
      lines = []
      for line in f:
        line_num += 1
        if line_num <= offset:
          continue
        if line_num > offset + limit:
          break
        lines.append(f"{line_num:6}\t{line}")
    return "".join(lines)
  except FileNotFoundError:
    return f"ERROR: file not found: /{path}"

def edit_file(path: str, old_string: str, new_string: str, replace_all: bool = False) -> str:
  """Perform an exact string replacement in a .md file.

  Args:
    path: Path to the file, starting with "/".
    old_string: The exact string to search for. Must appear exactly once unless
      replace_all is True.
    new_string: The string to replace old_string with.
    replace_all: If True, replace every occurrence of old_string. If False (default),
      errors when old_string appears more than once.
  """
  if ".." in path:
    return "ERROR: .. not permitted in path"

  if not path.endswith(".md"):
    return "ERROR: path must end in .md"

  if not path.startswith("/"):
    return "ERROR: path must start with /"
  
  if path in PROTECTED_PATHS:
    return f"ERROR: writes to {path} are not permitted"

  path = path[1:]

  abs_file_path = join(NOTES_PATH, path)

  try:
    with open(abs_file_path, 'r') as f:
      content = f.read()
  except FileNotFoundError:
    return f"ERROR: file not found: /{path}"

  count = content.count(old_string)

  if count == 0:
    return "ERROR: old_string not found in file"

  if not replace_all and count > 1:
    return f"ERROR: old_string found {count} times; use replace_all=True to replace all occurrences"

  new_content = content.replace(old_string, new_string) if replace_all else content.replace(old_string, new_string, 1)

  with open(abs_file_path, 'w') as f:
    f.write(new_content)

  replaced = count if replace_all else 1
  return f"OK: replaced {replaced} occurrence(s)"

def write_file(path: str, content: str) -> str:
  """Write content to a .md file, overwriting it if it exists or creating it if not.

  Args:
    path: Path to the file, starting with "/".
    content: Full content to write to the file.
  """
  if ".." in path:
    return "ERROR: .. not permitted in path"

  if not path.endswith(".md"):
    return "ERROR: path must end in .md"

  if not path.startswith("/"):
    return "ERROR: path must start with /"

  if path in PROTECTED_PATHS:
    return f"ERROR: writes to {path} are not permitted"

  path = path[1:]

  abs_file_path = join(NOTES_PATH, path)

  with open(abs_file_path, 'w') as f:
    f.write(content)

  return "OK: file written"

def glob_files(pattern: str, path: str = "/") -> str:
  """Find files matching a glob pattern within thew directory.
  Returns matching file paths sorted by modification time."""
  if ".." in path:
    return "ERROR: .. not permitted in path"

  if not path.startswith("/"):
    return "ERROR: path must start with /"

  abs_search_path = join(NOTES_PATH, path[1:])

  result = subprocess.run(
    ["rg", "--files", "--glob", pattern, abs_search_path],
    capture_output=True,
    text=True,
  )

  if result.returncode not in (0, 1):
    return f"ERROR: {result.stderr.strip()}"

  matches = result.stdout.splitlines()

  matches.sort(key=getmtime, reverse=True)

  relative = ["/" + m[len(NOTES_PATH):].lstrip("/") for m in matches]
  return "\n".join(relative)

def grep_files(
  pattern: str,
  path: str = "/",
  glob: str | None = None,
  output_mode: str = "files_with_matches",
  case_insensitive: bool = False,
  context: int = 0,
  multiline: bool = False,
) -> str:
  """Search for a regex pattern within the directory.

  Args:
    pattern: Regex pattern to search for.
    path: Directory or file to search in (default: "/").
    glob: Glob pattern to filter which files are searched (e.g. "*.md").
    output_mode: Controls what is returned:
      - "files_with_matches" (default): one path per line for each file that contains a match.
      - "content": matching lines with line numbers, in "<path>:<line>:<text>" format.
        When context > 0, non-matching context lines use "-" as separator and match
        groups are separated by "--".
      - "count": one "<path>:<n>" per file showing the number of matches.
    case_insensitive: If True, match regardless of case.
    context: Number of lines to show before and after each match (content mode only).
    multiline: If True, allow patterns to span multiple lines.
  """
  if ".." in path:
    return "ERROR: .. not permitted in path"

  if not path.startswith("/"):
    return "ERROR: path must start with /"

  abs_search_path = join(NOTES_PATH, path[1:])

  cmd = ["rg", pattern]

  if output_mode == "files_with_matches":
    cmd.append("--files-with-matches")
  elif output_mode == "count":
    cmd.append("--count")
  elif output_mode == "content":
    cmd.append("-n")
  else:
    return f"ERROR: unknown output_mode: {output_mode}"

  if case_insensitive:
    cmd.append("-i")

  if context > 0:
    cmd += ["-C", str(context)]

  if multiline:
    cmd += ["-U", "--multiline-dotall"]

  if glob:
    cmd += ["--glob", glob]

  cmd.append(abs_search_path)

  result = subprocess.run(cmd, capture_output=True, text=True)

  if result.returncode not in (0, 1):
    return f"ERROR: {result.stderr.strip()}"

  def strip_prefix(p):
    return "/" + p[len(NOTES_PATH):].lstrip("/")

  lines = result.stdout.splitlines()

  if output_mode == "files_with_matches":
    lines = [strip_prefix(l) for l in lines]
  else:
    processed = []
    for line in lines:
      if line == "--":
        processed.append(line)
      else:
        sep_idx = line.find(":")
        if sep_idx != -1 and line[:sep_idx].startswith(NOTES_PATH):
          line = strip_prefix(line[:sep_idx]) + line[sep_idx:]
        processed.append(line)
    lines = processed

  return "\n".join(lines)
