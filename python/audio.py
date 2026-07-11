import asyncio
import hashlib
import os
import re
import shutil
from pathlib import Path

import edge_tts


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
    """Trích xuất nội dung \\note{...}, xử lý ngoặc nhọn lồng nhau (nested braces),
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


# --- ĐOẠN CODE TẠO VÀ GHÉP AUDIO ---


# Hàm bất đồng bộ để gọi edge-tts
async def _create_edge_audio(text, output_file):
    # Sử dụng giọng nữ tiếng Việt mặc định của Microsoft (HoaiMy)
    communicate = edge_tts.Communicate(text, "vi-VN-HoaiMyNeural")
    await communicate.save(output_file)


def generate_and_merge_audio(results, base_output_dir_str):
    base_dir = Path(base_output_dir_str)

    # Khởi tạo thư mục chuck và merge
    chuck_dir = base_dir / "chuck"
    merge_dir = base_dir / "merge"
    chuck_dir.mkdir(parents=True, exist_ok=True)
    merge_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nBắt đầu tạo audio bằng Edge TTS...\n")
    print(f" - Thư mục file nhỏ: {chuck_dir}")
    print(f" - Thư mục file ghép: {merge_dir}\n")

    # Danh sách lưu các file đã merge theo đúng thứ tự
    ordered_merged_files = []

    for p, lines in results.items():
        print(f"-> Đang xử lý file: {Path(p).name}")

        chunk_files = []
        combined_text = ""

        # 1. Tạo các file nhỏ trong /chuck
        for line in lines:
            line_hash = hashlib.md5(line.encode("utf-8")).hexdigest()
            audio_file_path = chuck_dir / f"{line_hash}.mp3"

            # Lưu lại danh sách file nhỏ để ghép và text tổng để làm hash cho file merge
            chunk_files.append(audio_file_path)
            combined_text += line + "\n"

            if audio_file_path.exists():
                print(f"   [Đã có] chuck/{line_hash}.mp3")
                continue

            try:
                print(f"   [Tạo mới] chuck/{line_hash}.mp3 <- '{line[:30]}...'")
                asyncio.run(_create_edge_audio(line, str(audio_file_path)))
            except Exception as e:
                print(f"   [LỖI] Không thể tạo âm thanh: {e}")

        # 2. Ghép các file nhỏ thành file lớn trong /merge
        if chunk_files:
            # Sử dụng tên file latex gốc làm tên file merge thay vì dùng hash
            file_stem = Path(p).stem
            merged_file_path = merge_dir / f"{file_stem}.mp3"

            # Thêm vào danh sách theo thứ tự
            ordered_merged_files.append(merged_file_path)

            print(f" => Đang ghép các file thành: merge/{file_stem}.mp3")
            try:
                # Mở file merge ở chế độ ghi nhị phân (append/write binary)
                with open(merged_file_path, "wb") as outfile:
                    for chunk_path in chunk_files:
                        if chunk_path.exists():
                            # Đọc từng file nhỏ và nối thẳng dữ liệu vào file lớn
                            with open(chunk_path, "rb") as infile:
                                outfile.write(infile.read())
                print(f"    [Thành công] Đã lưu file merge!\n")
            except Exception as e:
                print(f"    [LỖI] Không thể ghép file: {e}\n")

    return ordered_merged_files


def create_final_master_audio(ordered_merged_files, final_audio_path):
    """Nối tất cả các file trong thư mục merge thành một file duy nhất"""
    print(f"\nĐang tiến hành ghép tổng thể thành file: {final_audio_path}")

    final_path = Path(final_audio_path)

    # Đảm bảo thư mục cha tồn tại
    final_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(final_path, "wb") as outfile:
            for mp3_file in ordered_merged_files:
                if mp3_file.exists():
                    with open(mp3_file, "rb") as infile:
                        outfile.write(infile.read())
        print(
            f"\n[HOÀN TẤT] File audio tổng hợp đã được lưu thành công tại:\n{final_audio_path}"
        )
    except Exception as e:
        print(f"\n[LỖI] Quá trình ghép file tổng hợp thất bại: {e}")


# Thực thi đoạn mã
if __name__ == "__main__":
    # --- XÓA THƯ MỤC CŨ TRƯỚC KHI CHẠY ---
    dir_to_remove = [
        Path(r"C:\Users\Admin\Documents\GitHub\docs-slide\audio\chuck"),
        Path(r"C:\Users\Admin\Documents\GitHub\docs-slide\audio\merge"),
    ]

    is_delete = False
    # is_delete = True

    if is_delete:
        print("Đang dọn dẹp các thư mục cũ...")
        for d in dir_to_remove:
            if d.exists() and d.is_dir():
                try:
                    shutil.rmtree(d)
                    print(f" [OK] Đã xóa thư mục: {d}")
                except Exception as e:
                    print(f" [LỖI] Không thể xóa thư mục {d}: {e}")
        print("-" * 70)

    # Đường dẫn file gốc
    file_path = r"C:\Users\Admin\Documents\GitHub\docs-slide\latex\doc.tex"
    # Thư mục lưu file audio (cho chuck và merge)
    audio_output_dir = r"C:\Users\Admin\Documents\GitHub\docs-slide\audio"
    # Đường dẫn file ghép tổng cuối cùng
    final_audio_file = r"C:\Users\Admin\Documents\GitHub\docs-slide\audio.mp3"

    # Bước 1: Trích xuất danh sách file
    paths = extract_tex_paths(file_path)

    print(f"Đang xử lý nội dung note từ {len(paths)} file...")
    print("=" * 70)

    # Bước 2: Trích xuất và làm sạch nội dung note
    results = extract_and_clean_notes(paths)

    # Bước 3: Tính mã băm, tạo file âm thanh nhỏ, và ghép thành file lớn trong /merge
    # Hàm này giờ đây sẽ trả về danh sách các file trong /merge theo đúng thứ tự
    ordered_files = generate_and_merge_audio(results, audio_output_dir)

    # Bước 4: Ghép tất cả các file merge lại thành file tổng audio.mp3
    if ordered_files:
        create_final_master_audio(ordered_files, final_audio_file)

    print("\n" + "=" * 70)
    print("Hoàn tất toàn bộ chu trình xử lý.")

    # Đường dẫn file (sử dụng đường dẫn hệ thống thay vì file:///)
    file_path = r"C:\Users\Admin\Documents\GitHub\docs-slide\audio.mp3"

    # Mở file bằng ứng dụng mặc định
    os.startfile(file_path)
