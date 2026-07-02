import os
import re
import subprocess


def compile_latex():
    try:
        # Biên dịch main.tex bằng pdflatex ở chế độ không tương tác (nonstopmode)
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "main.tex"],
            cwd="latex",
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=15,
        )
        return True
    except Exception as e:
        print(f"Lỗi hệ thống khi biên dịch: {e}")
        return False


def has_overflow():
    log_path = os.path.join("latex", "main.log")
    if not os.path.exists(log_path):
        return True

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        log_content = f.read()

    # Tìm đoạn log bắt đầu từ lúc tải file dev.tex
    idx = log_content.find("(dev.tex")
    if idx == -1:
        idx = log_content.find("(./dev.tex")

    if idx == -1:
        # Nếu không tìm thấy nhãn mở file, kiểm tra toàn bộ log làm dự phòng
        return "Overfull \\vbox" in log_content or "Overfull \\hbox" in log_content

    dev_log = log_content[idx:]

    # Chỉ quét log của dev.tex trước khi trình biên dịch chuyển sang đọc file tiếp theo (temp.tex)
    end_idx = dev_log.find("(temp.tex")
    if end_idx == -1:
        end_idx = dev_log.find("(./temp.tex")
    if end_idx != -1:
        dev_log = dev_log[:end_idx]

    return "Overfull \\vbox" in dev_log or "Overfull \\hbox" in dev_log


def main():
    input_path = os.path.join("latex", "temp.tex")
    output_path = os.path.join("latex", "dev.tex")

    if not os.path.exists(input_path):
        print(f"Không tìm thấy file nguồn: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Trích xuất slide đầu tiên từ temp.tex
    if r"\end{frame}" in content:
        first_frame = content.split(r"\end{frame}")[0] + r"\end{frame}"
    else:
        first_frame = content
    first_frame = first_frame.strip()

    print("=== BẮT ĐẦU TỰ ĐỘNG TÌM KÍCH THƯỚC ẢNH TỐI ƯU ===")

    optimal_size = 0.50
    # Quét từ 0.99 xuống 0.50 (bước nhảy 0.01) để lấy giá trị to nhất có thể
    for size_val in range(99, 49, -1):
        size = size_val / 100.0

        # Thay thế kích thước ảnh tạm thời trong dev.tex
        slide = re.sub(
            r"\\includegraphics\[[^\]]+\]",
            f"\\\\includegraphics[width=\\\\linewidth,height={size}\\\\textheight,keepaspectratio]",
            first_frame,
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(slide + "\n")

        # Biên dịch thử và kiểm tra kết quả trong log
        compile_latex()

        if not has_overflow():
            optimal_size = size
            print(f"[HỢP LỆ] Chiều cao {size} textheight không bị tràn khung.")
            break
        else:
            print(f"[TRÀN LỀ] Chiều cao {size} textheight làm slide bị quá kích thước.")

    # Ghi lại slide tối ưu hoàn chỉnh cuối cùng
    final_slide = re.sub(
        r"\\includegraphics\[[^\]]+\]",
        f"\\\\includegraphics[width=\\\\linewidth,height={optimal_size}\\\\textheight,keepaspectratio]",
        first_frame,
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_slide + "\n")

    # Biên dịch lại lần cuối cùng để cập nhật file PDF hoàn chỉnh
    compile_latex()
    print(
        f"\n=> HOÀN THÀNH: Đã tự động tìm và ghi kích thước tối ưu nhất là {optimal_size}\\textheight vào {output_path}"
    )


if __name__ == "__main__":
    main()
