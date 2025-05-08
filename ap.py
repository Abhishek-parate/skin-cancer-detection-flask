import os
from datetime import datetime
import subprocess

# File to update daily
file_to_update = "daily.txt"

# Write current timestamp to the file
with open(file_to_update, "a") as f:
    f.write(f"Commit made on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Git commands to add, commit, and push
commands = [
    ["git", "add", file_to_update],
    ["git", "commit", "-m", f"Daily commit: {datetime.now().strftime('%Y-%m-%d')}"],
    ["git", "push"]
]

# Execute commands
for command in commands:
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {' '.join(command)}")
        print(result.stderr)
        break
