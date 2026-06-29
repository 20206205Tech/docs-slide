# import os
# import shutil

# import env

# # import subprocess
# # import pyperclip


# new = "contents/Chuong 0/Tài liệu tham khảo/Tài liệu tham khảo"


# new = new.replace("Chuong 0", "Chương 0")


# def update_latex_document(file_path_doc, new_latex):
#     # Sử dụng raw string (r'...') để Python không hiểu nhầm dấu \ trong \input
#     target_string = r"\input{dev}"

#     # Mở và đọc toàn bộ nội dung file
#     with open(file_path_doc, "r", encoding="utf-8") as file:
#         content = file.read()

#     # Kiểm tra điều kiện và xử lý chuỗi
#     if target_string in content:
#         # Nếu có \input{dev}, thay thế bằng giá trị new_latex
#         updated_content = content.replace(target_string, new_latex)
#     else:
#         # Nếu không có, thêm new_latex vào cuối file (có kèm dấu xuống dòng để không bị dính chữ)
#         if not content.endswith("\n"):
#             content += "\n"
#         updated_content = content + new_latex

#     with open(file_path_doc, "w", encoding="utf-8") as file:
#         file.write(updated_content)


# def main():
#     file_path_new = os.path.join(env.PATH_FOLDER_LATEX, f"{new}.tex")
#     os.makedirs(os.path.dirname(file_path_new), exist_ok=True)

#     os.path.join(env.PATH_FOLDER_LATEX, "main.tex")
#     file_path_dev = os.path.join(env.PATH_FOLDER_LATEX, "dev.tex")
#     file_path_doc = os.path.join(env.PATH_FOLDER_LATEX, "doc.tex")

#     shutil.copyfile(file_path_dev, file_path_new)

#     with open(file_path_dev, "w") as f:
#         f.write("")

#     new_latex_content = f"\\input{{{new}}}" + "\n\\input{dev}"

#     update_latex_document(file_path_doc, new_latex_content)


# if __name__ == "__main__":
#     main()
