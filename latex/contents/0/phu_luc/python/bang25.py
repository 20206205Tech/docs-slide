import json
import os


def format_category(cat):
    """
    Formats the category name using LaTeX makecell for better line wrapping.
    """
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

    # Fallback and escaping
    return cat.replace("&", r"\&").replace("%", r"\%").replace("_", r"\_")


def write_latex_table(tex_path, stats):
    """
    Writes the 5-category statistics to bang25.tex.
    """
    lines = []
    lines.append(r"\begin{table}[H]")
    lines.append(r"\centering")
    lines.append(r"\refstepcounter{table}")
    lines.append(
        r"\textbf{Bảng \thetable:} Bảng thống kê chi tiết hiệu năng và độ chính xác theo từng kịch bản thử nghiệm"
    )
    lines.append(r"\label{tab:thong_ke_5_kich_ban}")
    lines.append(r"\vspace{0.5em}")
    lines.append(r"\begin{tabular}{|l|c|c|c|c|}")
    lines.append(r"\hline")
    lines.append(
        r"\makecell[l]{\textbf{Phân loại}\\\textbf{kịch bản}} & \makecell{\textbf{Tổng số}\\\textbf{câu hỏi}} & \makecell{\textbf{Phản hồi}\\\textbf{Đúng (\%)}} & \makecell{\textbf{Phản hồi Sai /}\\\textbf{Ảo giác (\%)}} & \makecell{\textbf{Không trả lời do}\\\textbf{không chắc chắn (\%)}} \\ \hline"
    )

    overall_total = 0
    overall_correct = 0
    overall_incorrect = 0
    overall_refused = 0

    # Ordered list of the 5 categories
    categories = [
        "Trong dữ liệu (Cơ bản)",
        "Trong dữ liệu (Nâng cao)",
        "Ngoài dữ liệu (Out-of-domain)",
        "Câu hỏi đánh lừa (Deceptive)",
        "Truy vấn mập mờ (Ambiguous)",
    ]

    for cat in categories:
        g_stats = stats.get(
            cat, {"total": 0, "CORRECT": 0, "INCORRECT_HALLUCINATION": 0, "REFUSED": 0}
        )
        total = g_stats["total"]

        correct = g_stats["CORRECT"]
        incorrect = g_stats["INCORRECT_HALLUCINATION"]
        refused = g_stats["REFUSED"]

        overall_total += total
        overall_correct += correct
        overall_incorrect += incorrect
        overall_refused += refused

        pct_correct = (correct / total) * 100 if total > 0 else 0
        pct_incorrect = (incorrect / total) * 100 if total > 0 else 0
        pct_refused = (refused / total) * 100 if total > 0 else 0

        cat_formatted = format_category(cat)

        row = f"{cat_formatted} & {total} & {correct} ({pct_correct:.1f}\\%) & {incorrect} ({pct_incorrect:.1f}\\%) & {refused} ({pct_refused:.1f}\\%) \\\\ \\hline"
        lines.append(row)

    if overall_total > 0:
        pct_o_correct = (overall_correct / overall_total) * 100
        pct_o_incorrect = (overall_incorrect / overall_total) * 100
        pct_o_refused = (overall_refused / overall_total) * 100

        overall_row = (
            f"\\textbf{{Tổng cộng (Overall)}} & \\textbf{{{overall_total}}} & "
            f"\\textbf{{{overall_correct} ({pct_o_correct:.1f}\\%)}} & "
            f"\\textbf{{{overall_incorrect} ({pct_o_incorrect:.1f}\\%)}} & "
            f"\\textbf{{{overall_refused} ({pct_o_refused:.1f}\\%)}} \\\\ \\hline"
        )
        lines.append(overall_row)

    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    eval_path = os.path.join(script_dir, "evaluation_detail.json")
    tex_path = os.path.join(script_dir, "bang25.tex")

    if not os.path.exists(eval_path):
        print(
            f"Error: {eval_path} not found. Vui lòng chạy bang2.py trước để sinh file đánh giá chi tiết."
        )
        return

    print(f"Đang đọc dữ liệu đánh giá từ {eval_path}...")
    with open(eval_path, "r", encoding="utf-8") as f:
        eval_results = json.load(f)

    # Initialize statistics for the 5 categories
    stats = {
        "Trong dữ liệu (Cơ bản)": {
            "total": 0,
            "CORRECT": 0,
            "INCORRECT_HALLUCINATION": 0,
            "REFUSED": 0,
        },
        "Trong dữ liệu (Nâng cao)": {
            "total": 0,
            "CORRECT": 0,
            "INCORRECT_HALLUCINATION": 0,
            "REFUSED": 0,
        },
        "Ngoài dữ liệu (Out-of-domain)": {
            "total": 0,
            "CORRECT": 0,
            "INCORRECT_HALLUCINATION": 0,
            "REFUSED": 0,
        },
        "Câu hỏi đánh lừa (Deceptive)": {
            "total": 0,
            "CORRECT": 0,
            "INCORRECT_HALLUCINATION": 0,
            "REFUSED": 0,
        },
        "Truy vấn mập mờ (Ambiguous)": {
            "total": 0,
            "CORRECT": 0,
            "INCORRECT_HALLUCINATION": 0,
            "REFUSED": 0,
        },
    }

    # Aggregate statistics
    for item in eval_results:
        cat = item.get("phan_loai_goc")
        if not cat:
            continue

        verdict = item.get("danh_gia", {}).get("ket_luan", "REFUSED")

        if cat in stats:
            stats[cat]["total"] += 1
            stats[cat][verdict] += 1

    print("Thống kê thu thập được:")
    for cat, data in stats.items():
        print(f" - {cat}: {data}")

    print(f"Đang ghi bảng thống kê 5 nhóm vào {tex_path}...")
    write_latex_table(tex_path, stats)
    print("Đã tạo bảng bang25.tex thành công!")


if __name__ == "__main__":
    main()
