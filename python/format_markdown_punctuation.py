import re
import sys
from pathlib import Path

# Ensure console output handles UTF-8 for Vietnamese characters
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)


def format_punctuation(content):
    # Skip code blocks (``` ... ```) and inline code (`...`)
    parts = re.split(r"(```[\s\S]*?```|`[^`]*?`)", content)

    for i in range(len(parts)):
        # Only format parts that are NOT code blocks or inline code
        if not (parts[i].startswith("```") or parts[i].startswith("`")):
            # The user requested to only handle commas (,)

            # 1. Handle Comma (no space before, one space after)
            parts[i] = re.sub(r"\s*,\s*", ",", parts[i])
            parts[i] = re.sub(r",(?!\s|$)", ", ", parts[i])

            # 2. Fix-up: Restore URLs and Windows paths broken by previous colon formatting
            # (Only fixing what was broken, not adding new formatting)
            parts[i] = re.sub(r"(https?|ftp)\s*:\s*//", r"\1://", parts[i])
            parts[i] = re.sub(r"([a-zA-Z])\s*:\s*\\", r"\1:\\", parts[i])

            # 3. Terminology replacement
            parts[i] = parts[i].replace("hội thoại", "trò chuyện")
            parts[i] = parts[i].replace("HỘI THOẠI", "TRÒ CHUYỆN")

    return "".join(parts)


def process_docs():
    docs_dir = Path("docs")
    if not docs_dir.exists():
        print("Directory 'docs' not found.")
        return

    for md_file in docs_dir.rglob("*.md"):
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            formatted_content = format_punctuation(content)

            if content != formatted_content:
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(formatted_content)
                print(f"Updated: {md_file}")
            else:
                pass  # No changes needed
        except Exception as e:
            print(f"Error processing {md_file}: {e}")


if __name__ == "__main__":
    process_docs()
