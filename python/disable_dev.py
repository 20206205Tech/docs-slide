import os

# Lấy đường dẫn tương đối tới script
script_dir = os.path.dirname(os.path.abspath(__file__))
main_tex_path = os.path.abspath(os.path.join(script_dir, "..", "latex", "main.tex"))

if not os.path.exists(main_tex_path):
    # Thử ở thư mục hiện tại
    main_tex_path = os.path.abspath("latex/main.tex")

if not os.path.exists(main_tex_path):
    raise FileNotFoundError(f"Không tìm thấy main.tex tại {main_tex_path}")

with open(main_tex_path, "r", encoding="utf-8") as f:
    content = f.read()

# Thay thế \devtrue thành \devfalse
if "\\devtrue" in content:
    new_content = content.replace("\\devtrue", "\\devfalse")
    with open(main_tex_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Đã vô hiệu hóa dev mode thành công (thay \\devtrue thành \\devfalse).")
else:
    print("Dev mode đã được vô hiệu hóa từ trước hoặc không tìm thấy \\devtrue.")
