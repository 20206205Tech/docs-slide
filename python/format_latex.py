import re
import sys

import env

# Ensure console output handles UTF-8 for Vietnamese characters
if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)


def format_terminology(content):
    # 1. Strip invisible/zero-width characters from the entire content first
    #    (these appear anywhere, including inside LaTeX commands — safe to remove globally)
    INVISIBLE_CHARS = [
        "\u200B",  # Zero Width Space
        "\u200C",  # Zero Width Non-Joiner
        "\u200D",  # Zero Width Joiner
        "\uFEFF",  # BOM / Zero Width No-Break Space
        "\u00AD",  # Soft Hyphen
    ]
    for char in INVISIBLE_CHARS:
        content = content.replace(char, "")

    # 2. Strip trailing/leading whitespace from every line
    lines = content.split("\n")
    content = "\n".join(line.strip() for line in lines)

    # 3. Collapse multiple spaces into one
    while "  " in content:
        content = content.replace("  ", " ")

    # 4. Join \item followed by a newline + content onto one line
    #    e.g. "\item\nFoo" -> "\item Foo"
    content = re.sub(r"(\\item)\n+(\S)", r"\1 \2", content)

    # 5. Collapse 3+ consecutive newlines down to 2
    while "\n\n\n" in content:
        content = content.replace("\n\n\n", "\n\n")

    content = content.replace("GitHub Action", "GitHub Actions")
    while "GitHub Actionss" in content:
        content = content.replace("GitHub Actionss", "GitHub Actions")
    # 6. Terminology replacement — skip LaTeX comments (% not preceded by \)
    lines = content.split("\n")
    result = []

    for line in lines:
        # Find where the comment starts
        comment_idx = -1
        for i, ch in enumerate(line):
            if ch == "%" and (i == 0 or line[i - 1] != "\\"):
                comment_idx = i
                break

        if comment_idx == -1:
            text_part = line
            comment_part = ""
        else:
            text_part = line[:comment_idx]
            comment_part = line[comment_idx:]

        # Terminology replacement (add your terms below)
        text_part = text_part.replace("hội thoại", "trò chuyện")
        text_part = text_part.replace("HỘI THOẠI", "TRÒ CHUYỆN")

        text_part = text_part.replace("phiên trò chuyện", "cuộc trò chuyện")
        # text_part = text_part.replace("cơ sở dữ liệu", "CSDL")
        text_part = text_part.replace(" ,", ",")
        text_part = text_part.replace(", và", " và")
        text_part = text_part.replace("; và", " và")
        # text_part = text_part.replace("} ", "}\n")

        # text_part = text_part.replace("LiveKit", "LiveKit")
        # text_part = text_part.replace("livekit", "LiveKit")

        result.append(text_part + comment_part)

    return "\n".join(result).strip() + "\n"


def process_latex():
    latex_dir = env.PATH_FOLDER_LATEX

    if not latex_dir or not __import__("os").path.exists(latex_dir):
        print(f"Directory not found: {latex_dir}")
        return

    from pathlib import Path

    for tex_file in Path(latex_dir).rglob("*.tex"):
        try:
            with open(tex_file, "r", encoding="utf-8") as f:
                content = f.read()

            formatted_content = format_terminology(content)

            if content != formatted_content:
                with open(tex_file, "w", encoding="utf-8") as f:
                    f.write(formatted_content)
                print(f"Updated: {tex_file}")
        except Exception as e:
            print(f"Error processing {tex_file}: {e}")


if __name__ == "__main__":
    process_latex()
