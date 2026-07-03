import os
import re
import subprocess


def compile_latex():
    try:
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


def get_overflow_lines():
    log_path = os.path.join("latex", "main.log")
    if not os.path.exists(log_path):
        return set()

    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        log_content = f.read()

    # Cô lập phần log của dev.tex
    idx = log_content.find("(dev.tex")
    if idx == -1:
        idx = log_content.find("(./dev.tex")

    if idx == -1:
        dev_log = log_content
    else:
        dev_log = log_content[idx:]
        end_idx = dev_log.find("(temp.tex")
        if end_idx == -1:
            end_idx = dev_log.find("(./temp.tex")
        if end_idx != -1:
            dev_log = dev_log[:end_idx]

    overflow_lines = set()
    # Tìm dòng bị cảnh báo Overfull \vbox
    for m in re.finditer(r"detected at line (\d+)", dev_log):
        overflow_lines.add(int(m.group(1)))
    # Tìm dòng bị cảnh báo Overfull \hbox
    for m in re.finditer(r"at lines (\d+)(?:--\d+)?", dev_log):
        overflow_lines.add(int(m.group(1)))

    return overflow_lines


def main():
    input_path = os.path.join("latex", "temp.tex")
    output_path = os.path.join("latex", "dev.tex")

    if not os.path.exists(input_path):
        print(f"Không tìm thấy file nguồn: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    if r"\end{frame}" in content:
        first_frame = content.split(r"\end{frame}")[0] + r"\end{frame}"
    else:
        first_frame = content
    first_frame = first_frame.strip()

    print("=== BẮT ĐẦU TỐI ƯU HÓA SIÊU TỐC (CHỈ BIÊN DỊCH 1 LẦN) ===")

    # Phát hiện cấu trúc và số lượng ảnh trong slide
    num_images = len(re.findall(r"\\includegraphics", first_frame))
    is_parallel = r"\begin{columns}" in first_frame
    print(
        f"Phát hiện: {num_images} ảnh. Cấu trúc xếp song song (columns): {is_parallel}"
    )

    slides = []
    sizes = [val / 100.0 for val in range(50, 100)]

    for size in sizes:
        # Xác định chiều cao tối đa cho mỗi ảnh dựa trên cấu trúc slide
        if is_parallel or num_images <= 1:
            img_height = size
        else:
            # Nếu xếp dọc, chia đều chiều cao tối đa của vùng thử nghiệm cho số lượng ảnh
            img_height = size / num_images

        # Thay đổi kích thước ảnh cho từng trường hợp thử nghiệm (khớp cả trường hợp có hoặc không có [options] sẵn)
        slide = re.sub(
            r"\\includegraphics(?:\[[^\]]*\])?",
            f"\\\\includegraphics[width=\\\\linewidth,height={img_height:.3f}\\\\textheight,keepaspectratio]",
            first_frame,
        )
        slides.append(slide)

    # Nối tất cả các slide lại bằng 2 dấu xuống dòng
    file_content = "\n\n".join(slides) + "\n"

    # Xác định chính xác khoảng dòng của mỗi slide bằng cách đếm dòng thực tế
    slide_ranges = []
    line_index = 0
    for idx, size in enumerate(sizes):
        slide_lines = slides[idx].splitlines()
        num_lines = len(slide_lines)

        start_line = line_index + 1
        end_line = line_index + num_lines

        slide_ranges.append(
            {"size": size, "start_line": start_line, "end_line": end_line}
        )

        # dịch chuyển vị trí dòng tiếp theo (cộng thêm 1 cho dòng trống phân tách)
        line_index += num_lines + 1

    # Ghi toàn bộ 50 slide thử nghiệm vào dev.tex để kiểm tra đồng thời
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(file_content)

    print("Đang biên dịch đồng thời 50 slide thử nghiệm...")
    compile_latex()

    # Đọc log để xem dòng nào bị tràn lề
    overflow_lines = get_overflow_lines()
    print(f"Các dòng bị báo lỗi tràn trong dev.tex: {sorted(list(overflow_lines))}")

    # Xác định các kích thước bị tràn lề
    overflow_sizes = set()
    for line in overflow_lines:
        for r in slide_ranges:
            if r["start_line"] <= line <= r["end_line"]:
                overflow_sizes.add(r["size"])

    # Chọn kích thước lớn nhất mà KHÔNG bị tràn lề
    valid_sizes = [size for size in sizes if size not in overflow_sizes]

    if valid_sizes:
        optimal_size = max(valid_sizes)
        print(f"-> Kích thước tối ưu lớn nhất tìm thấy: {optimal_size}")
    else:
        optimal_size = 0.50
        print(
            "-> Tất cả kích thước đều bị tràn lề, tự động chọn kích thước an toàn tối thiểu 0.50"
        )

    # Ghi lại một slide duy nhất với kích thước tối ưu vào dev.tex
    if is_parallel or num_images <= 1:
        optimal_img_height = optimal_size
    else:
        optimal_img_height = optimal_size / num_images

    final_slide = re.sub(
        r"\\includegraphics(?:\[[^\]]*\])?",
        f"\\\\includegraphics[width=\\\\linewidth,height={optimal_img_height:.3f}\\\\textheight,keepaspectratio]",
        first_frame,
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(final_slide + "\n")

    # Biên dịch lại lần cuối để đồng bộ file PDF
    compile_latex()
    print(
        f"\n=> HOÀN THÀNH: Đã ghi kích thước tối ưu {optimal_size}\\textheight vào {output_path}"
    )


if __name__ == "__main__":
    main()
