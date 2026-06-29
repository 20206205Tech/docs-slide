import json
import os


def escape_latex(text):
    if not isinstance(text, str):
        return str(text)
    # Escape LaTeX special characters
    # Order matters: backslash must be first, then others
    text = text.replace("\\", r"\textbackslash{}")
    for char in ["&", "%", "$", "#", "_", "{", "}"]:
        text = text.replace(char, "\\" + char)
    text = text.replace("~", r"\textasciitilde{}")
    text = text.replace("^", r"\textasciicircum{}")
    # Replace newlines with space to avoid breaking LaTeX table rows
    text = text.replace("\n", " ")
    return text


def format_category(cat):
    if "Cơ bản" in cat:
        return r"\makecell[l]{Trong dữ liệu\\(Cơ bản)}"
    elif "Nâng cao" in cat:
        return r"\makecell[l]{Trong dữ liệu\\(Nâng cao)}"
    elif "Out-of-domain" in cat:
        return r"\makecell[l]{Ngoài dữ liệu\\(Out-of-domain)}"
    elif "Deceptive" in cat:
        return r"\makecell[l]{Câu hỏi đánh lừa\\(Deceptive)}"
    elif "Ambiguous" in cat:
        return r"\makecell[l]{Truy vấn mập mờ\\(Ambiguous)}"
    return escape_latex(cat)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, "result.json")
    tex_path = os.path.join(script_dir, "bang1.tex")

    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    print(f"Reading data from {json_path}...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data)} test cases. Generating LaTeX table...")

    lines = []
    lines.append(r"\begin{longtable}{|c|l|p{6.5cm}|c|c|}")
    lines.append(
        r"\caption{Bảng thống kê chi tiết các kịch bản thử nghiệm hệ thống} \label{tab:thong_ke_chi_tiet} \\"
    )
    lines.append(r"\hline")
    lines.append(
        r"\textbf{STT} & \makecell[l]{\textbf{Phân loại}\\\textbf{trường hợp}} & \textbf{Câu hỏi} & \makecell{\textbf{Tài liệu}\\\textbf{truy xuất}} & \textbf{Thời gian} \\ \hline"
    )
    lines.append(r"\endfirsthead")

    lines.append(
        r"\multicolumn{5}{c}{{\bfseries Bảng \thetable{} -- Tiếp theo từ trang trước}} \\"
    )
    lines.append(r"\hline")
    lines.append(
        r"\textbf{STT} & \makecell[l]{\textbf{Phân loại}\\\textbf{trường hợp}} & \textbf{Câu hỏi} & \makecell{\textbf{Tài liệu}\\\textbf{truy xuất}} & \textbf{Thời gian} \\ \hline"
    )
    lines.append(r"\endhead")

    lines.append(r"\hline")
    lines.append(r"\multicolumn{5}{r}{{Tiếp tục ở trang sau}} \\")
    lines.append(r"\endfoot")

    lines.append(r"\hline")
    lines.append(r"\endlastfoot")

    for item in data:
        stt = item.get("stt", "")
        phan_loai = item.get("phan_loai", "")
        cau_hoi = item.get("cau_hoi", "")

        # Count number of retrieved documents
        num_docs = len(item.get("tai_lieu_raw", []))
        docs_str = f"{num_docs} tài liệu"

        time_str = item.get("thoi_gian_xu_ly", "")

        # Format values for LaTeX
        cat_formatted = format_category(phan_loai)
        q_escaped = escape_latex(cau_hoi)
        docs_escaped = escape_latex(docs_str)
        time_escaped = escape_latex(time_str)

        row = f"{stt} & {cat_formatted} & {q_escaped} & {docs_escaped} & {time_escaped} \\\\ \\hline"
        lines.append(row)

    lines.append(r"\end{longtable}")

    print(f"Writing LaTeX table to {tex_path}...")
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print("Successfully generated bang1.tex!")


if __name__ == "__main__":
    main()
