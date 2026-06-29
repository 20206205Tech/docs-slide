import os

import env


def delete_empty_file(directory):
    print(f"Format markdown gui with root folder = {os.path.abspath(directory)}")

    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".tex"):
                file_path = os.path.join(root, file)
                print(f"Processing file: {file_path}")

                try:
                    # Sử dụng file_path thay vì full_path
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    if content.strip() == "":
                        os.remove(file_path)
                        print(f"Deleted file: {file_path}")
                    else:
                        print(f"File {file_path} is not empty")

                except Exception as e:
                    print(f"Error reading/deleting {file_path}: {e}")


def main():
    target_dir = os.path.join(env.PATH_FOLDER_LATEX, "contents")

    # Kiểm tra xem thư mục có tồn tại trước khi chạy không
    if os.path.exists(target_dir):
        delete_empty_file(target_dir)
    else:
        print(f"Error: Thư mục không tồn tại - {target_dir}")


if __name__ == "__main__":
    main()
