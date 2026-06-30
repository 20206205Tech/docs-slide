import os


def split_latex(input_file, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    chunks = []
    current_frame = []
    in_frame = False

    for line in lines:
        stripped = line.strip()
        if in_frame:
            current_frame.append(line)
            # Check if it is the end of the frame
            if stripped.startswith(r"\end{frame}"):
                chunks.append("\n".join(current_frame))
                current_frame = []
                in_frame = False
        else:
            if stripped.startswith(r"\section"):
                chunks.append(line)
            elif stripped.startswith(r"\subsection"):
                chunks.append(line)
            elif stripped.startswith(r"\begin{frame}"):
                in_frame = True
                current_frame.append(line)
            # Any other lines (like empty lines or comments outside of frames) are ignored
            # to keep the split files clean.

    # Write chunks to files 1.tex, 2.tex, ...
    for i, chunk in enumerate(chunks, 1):
        out_path = os.path.join(output_dir, f"{i}.tex")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(chunk + "\n")
        print(f"Saved: {out_path}")


if __name__ == "__main__":
    input_file = r"C:\Users\Admin\Documents\GitHub\docs-slide\latex\dev.tex"
    output_dir = r"C:\Users\Admin\Documents\GitHub\docs-slide\latex\temp"
    split_latex(input_file, output_dir)
