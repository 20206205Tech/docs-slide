import hashlib
import re
from pathlib import Path

import pyttsx3


def extract_tex_paths(doc_file_path):
    doc_path = Path(doc_file_path)
    base_dir = doc_path.parent

    try:
        with open(doc_path, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Không tìm thấy file: {doc_path}")
        return []

    content_no_comments = re.sub(r"%.*$", "", content, flags=re.MULTILINE)
    pattern = re.compile(r"\\input\{([^}]+)\}")
    matches = pattern.findall(content_no_comments)

    full_paths = []
    for match in matches:
        file_name = match if match.endswith(".tex") else f"{match}.tex"
        full_path = base_dir / file_name
        full_paths.append(str(full_path))

    return full_paths


def extract_and_clean_notes(file_paths):
    """Trích xuất nội dung \note{...}, xử lý ngoặc nhọn lồng nhau (nested braces),

    và làm sạch văn bản theo yêu cầu.
    """
    all_cleaned_lines = {}

    for path in file_paths:
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            notes_content = []
            idx = 0

            # 1. Trích xuất toàn bộ khối \note{...}
            while True:
                start_idx = content.find(r"\note{", idx)
                if start_idx == -1:
                    break

                open_braces = 0
                content_start = start_idx + 6  # Bỏ qua chuỗi '\note{'
                content_end = -1

                # Duyệt từng ký tự để tìm dấu ngoặc đóng tương ứng
                for i in range(content_start, len(content)):
                    if content[i] == "{":
                        open_braces += 1
                    elif content[i] == "}":
                        if open_braces == 0:
                            content_end = i
                            break
                        else:
                            open_braces -= 1

                if content_end != -1:
                    notes_content.append(content[content_start:content_end])
                    idx = content_end + 1
                else:
                    idx = (
                        content_start + 6
                    )  # Nếu lỗi cú pháp thiếu ngoặc, bỏ qua và đi tiếp

            # 2. Xử lý làm sạch nội dung
            cleaned_lines = []
            for note in notes_content:
                # Bỏ nội dung comment (bắt đầu bằng %)
                note = re.sub(r"%.*$", "", note, flags=re.MULTILINE)

                # Tách thành từng dòng
                lines = note.split("\n")
                for line in lines:
                    # Bỏ \hrule và xóa khoảng trắng thừa ở 2 đầu
                    line = line.replace(r"\hrule", "").strip()

                    # Bỏ qua các dòng rỗng
                    if line:
                        cleaned_lines.append(line)

            if cleaned_lines:
                all_cleaned_lines[path] = cleaned_lines

        except FileNotFoundError:
            print(f"[LỖI] Không tìm thấy file: {path}")
        except Exception as e:
            print(f"[LỖI] Lỗi đọc file {path}: {e}")

    return all_cleaned_lines


# --- ĐOẠN CODE THÊM MỚI: TÍNH MÃ BĂM VÀ TẠO AUDIO ---


def generate_audio_from_lines(results, output_dir_str):
    """Tính mã băm md5 cho từng dòng và dùng pyttsx3 để xuất thành file audio."""
    output_dir = Path(output_dir_str)
    output_dir.mkdir(parents=True, exist_ok=True)  # Tạo thư mục nếu chưa có

    # Khởi tạo engine pyttsx3
    engine = pyttsx3.init()

    # Cài đặt tốc độ nói (tùy chỉnh nếu cần, mặc định thường là 200)
    engine.setProperty("rate", 180)

    print(f"\nBắt đầu tạo audio và lưu vào: {output_dir}\n")

    for p, lines in results.items():
        print(f"-> Đang xử lý file: {Path(p).name}")
        for line in lines:
            # 1. Tính mã băm MD5 từ nội dung dòng (chuẩn hóa UTF-8)
            # Mã băm MD5 luôn có độ dài cố định 32 ký tự Hex
            line_hash = hashlib.md5(line.encode("utf-8")).hexdigest()

            # Định dạng tên file: bằng mã băm
            audio_file_path = output_dir / f"{line_hash}.mp3"

            # Kiểm tra nếu file đã tồn tại thì bỏ qua (tiết kiệm thời gian chạy lại)
            if audio_file_path.exists():
                print(f"   [Đã có] {line_hash}.mp3 <- '{line[:30]}...'")
                continue

            # 2. Tạo file âm thanh từ text
            try:
                print(f"   [Tạo mới] {line_hash}.mp3 <- '{line[:30]}...'")
                engine.save_to_file(line, str(audio_file_path))
                # Phải gọi runAndWait() để pyttsx3 thực hiện việc ghi file
                engine.runAndWait()
            except Exception as e:
                print(f"   [LỖI] Không thể tạo âm thanh cho dòng '{line}': {e}")


# Thực thi đoạn mã
if __name__ == "__main__":
    # Đường dẫn file gốc
    file_path = r"C:\Users\Admin\Documents\GitHub\docs-slide\latex\doc.tex"
    # Thư mục lưu file audio theo yêu cầu
    audio_output_dir = r"C:\Users\Admin\Documents\GitHub\docs-slide\audio"

    # Bước 1: Trích xuất danh sách file
    paths = extract_tex_paths(file_path)

    print(f"Đang xử lý nội dung note từ {len(paths)} file...")
    print("=" * 70)

    # Bước 2: Trích xuất và làm sạch nội dung note
    results = extract_and_clean_notes(paths)

    # Bước 3: Tính mã băm và tạo file âm thanh
    generate_audio_from_lines(results, audio_output_dir)

    print("\n" + "=" * 70)
    print("Hoàn tất quá trình trích xuất và tạo âm thanh.")
