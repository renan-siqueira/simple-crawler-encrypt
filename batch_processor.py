import subprocess
import config
import sys

python_executable = sys.executable


def batch_process():
    with open(config.PATH_OUTPUT_FILE, 'r') as file:
        for line in file:
            url = line.strip()
            if url:
                subprocess.run([python_executable, "main.py", "--url", url, "--batch"])


if __name__ == "__main__":
    batch_process()
