from pathlib import Path

import env

NOTE_START = r"\note{"
FRAME_END = r"\end{frame}"


def lowercase_note_text(content):
    result = []
    cursor = 0

    while True:
        note_start = content.find(NOTE_START, cursor)
        if note_start == -1:
            result.append(content[cursor:])
            break

        note_text_start = note_start + len(NOTE_START)
        frame_end = content.find(FRAME_END, note_text_start)
        if frame_end == -1:
            result.append(content[cursor:])
            break

        result.append(content[cursor:note_text_start])
        result.append(content[note_text_start:frame_end].lower())
        cursor = frame_end

    return "".join(result)


def process_latex():
    latex_dir = Path(env.PATH_FOLDER_LATEX)

    if not latex_dir.exists():
        print(f"Directory not found: {latex_dir}")
        return

    for tex_file in latex_dir.rglob("*.tex"):
        try:
            content = tex_file.read_text(encoding="utf-8")
            formatted_content = lowercase_note_text(content)

            if content != formatted_content:
                tex_file.write_text(formatted_content, encoding="utf-8")
                print(f"Updated: {tex_file}")
        except Exception as e:
            print(f"Error processing {tex_file}: {e}")


if __name__ == "__main__":
    process_latex()
