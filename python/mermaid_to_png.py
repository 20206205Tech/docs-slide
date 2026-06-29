import base64
import os
import sys

import requests


def mermaid_to_image(mermaid_code: str, output_file: str):
    """Converts Mermaid code to a PNG image using the mermaid.ink API."""
    # 1. Encode Mermaid string to Base64 (URL-safe)
    graphbytes = mermaid_code.encode("utf-8")
    base64_bytes = base64.urlsafe_b64encode(graphbytes)
    base64_string = base64_bytes.decode("utf-8").replace("=", "")

    # 2. Create API URL
    url = f"https://mermaid.ink/img/{base64_string}"

    # 3. Call API and download image
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"Successfully saved image at: {output_file}")
        else:
            print(f"Error downloading image: {response.status_code}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    # Set stdout to use UTF-8 to handle Vietnamese characters in paths
    if sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except AttributeError:
            # Fallback for older python versions if any
            pass

    if len(sys.argv) < 2:
        print("Usage: python mermaid_to_png.py <file1.mmd> <file2.mmd> ...")
        sys.exit(1)

    for mmd_file in sys.argv[1:]:
        if not os.path.exists(mmd_file):
            print(f"File not found: {mmd_file}")
            continue

        if not mmd_file.endswith(".mmd"):
            print(f"Skipping non-mmd file: {mmd_file}")
            continue

        print(f"Processing {mmd_file}...")
        try:
            with open(mmd_file, "r", encoding="utf-8") as f:
                code = f.read()

            output_file = os.path.splitext(mmd_file)[0] + ".png"
            mermaid_to_image(code, output_file)
        except Exception as e:
            print(f"Failed to process {mmd_file}: {e}")


if __name__ == "__main__":
    main()
