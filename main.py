import os
import re


def main():
    # Đường dẫn tới file input (temp.tex) và output (dev.tex)
    input_path = os.path.join("latex", "temp.tex")
    output_path = os.path.join("latex", "dev.tex")

    # Kiểm tra sự tồn tại của file input
    if not os.path.exists(input_path):
        print(f"Không tìm thấy file nguồn: {input_path}")
        return

    try:
        # Đọc nội dung từ file temp.tex
        with open(input_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Chỉ lấy frame đầu tiên
        if r"\end{frame}" in content:
            first_frame = content.split(r"\end{frame}")[0] + r"\end{frame}"
        else:
            first_frame = content

        first_frame = first_frame.strip()

        # Sơ đồ Use Case không có text list đi kèm nên không gian trống dọc nhiều hơn.
        # Qua thực nghiệm biên dịch log, chiều cao tối đa đạt được là 0.65\textheight.
        optimal_slide = re.sub(
            r"\\includegraphics\[[^\]]+\]",
            r"\\includegraphics[width=\\linewidth,height=0.65\\textheight,keepaspectratio]",
            first_frame,
        )

        # Ghi nội dung slide tối ưu duy nhất vào dev.tex
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(optimal_slide + "\n")

        print(
            f"Thành công! Đã lưu slide tối ưu duy nhất (height=0.65) vào {output_path}"
        )

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")


if __name__ == "__main__":
    main()
