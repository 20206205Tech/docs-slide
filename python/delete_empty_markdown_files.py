import os
import sys

# Ensure terminal output supports UTF-8 for Vietnamese characters
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        # Fallback for older Python versions
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def delete_empty_markdown_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if not content.strip():
                        print(f"Deleting empty markdown file: {file_path}")
                        os.remove(file_path)
                except Exception as e:
                    print(f"Error processing {file_path}: {repr(e)}")


if __name__ == "__main__":
    # Scan from the 'docs' directory for safety
    target_directory = "docs"

    if not os.path.exists(target_directory):
        print(f"Directory not found: {target_directory}")
        sys.exit(0)

    print(f"Scanning for empty markdown files in: {os.path.abspath(target_directory)}")
    delete_empty_markdown_files(target_directory)
