import os
import sys

import env

# Ensure terminal output supports UTF-8 for Vietnamese characters
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def delete_empty_latex_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if os.path.basename(file) == "dev.tex":
                continue
            if file.endswith(".tex"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if not content.strip():
                        print(f"Deleting empty latex file: {file_path}")
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error processing {file_path}: {repr(e)}")


if __name__ == "__main__":
    target_directory = env.PATH_FOLDER_LATEX

    if not os.path.exists(target_directory):
        print(f"Directory not found: {target_directory}")
        sys.exit(0)

    print(f"Scanning for empty latex files in: {os.path.abspath(target_directory)}")
    delete_empty_latex_files(target_directory)
