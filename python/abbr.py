import os
import re
import sys

import env

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except AttributeError:
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)


DATA = [
    # {"abbr": "GPU", "eng": "Graphics Processing Unit", "vie": "Bộ phận xử lý đồ họa"},
    {"abbr": "AI", "eng": "Artificial Intelligence", "vie": "Trí tuệ nhân tạo"},
    {
        "abbr": "NLP",
        "eng": "Natural Language Processing",
        "vie": "Xử lý ngôn ngữ tự nhiên",
    },
    {"abbr": "LLM", "eng": "Large Language Model", "vie": "Mô hình ngôn ngữ lớn"},
    {
        "abbr": "API",
        "eng": r"\makecell[l]{Application Programming \\ Interface}",
        "vie": "Giao diện lập trình ứng dụng",
    },
    {
        "abbr": "RAG",
        "eng": r"\makecell[l]{Retrieval Augmented \\ Generation}",
        "vie": "Tạo tăng cường truy xuất",
    },
    {"abbr": "DDD", "eng": "Domain Driven Design", "vie": "Thiết kế hướng miền"},
    # {"abbr": "MSA", "eng": "Microservice Architecture", "vie": "Kiến trúc vi dịch vụ"},
    {
        "abbr": "SQL",
        "eng": "Structured Query Language",
        "vie": "Ngôn ngữ truy vấn cấu trúc",
    },
    {
        "abbr": "JWT",
        "eng": "JSON Web Token",
        "vie": "Tiêu chuẩn truyền tải thông tin JSON",
    },
    # {
    #     "abbr": "JSON",
    #     "eng": "JavaScript Object Notation",
    #     "vie": "Một kiểu định dạng dữ liệu key - value",
    # },
    {
        "abbr": "RLS",
        "eng": "Row-Level Security",
        "vie": "Bảo mật cấp hàng",
    },
    # {
    #     "abbr": "OOP",
    #     "eng": "Object-Oriented Programming",
    #     "vie": "Lập trình hướng đối tượng",
    # },
    {"abbr": "CLI", "eng": "Command Line Interface", "vie": "Giao diện dòng lệnh"},
    {"abbr": "CSDL", "eng": "Cơ sở dữ liệu", "vie": "Cơ sở dữ liệu"},
    {"abbr": "SSE", "eng": "Server-sent events", "vie": "Sự kiện máy chủ gửi"},
    {
        "abbr": "TOTP",
        "eng": r"\makecell[l]{Time-based \\ One-Time Password}",
        "vie": r"\makecell[l]{Mật khẩu dùng một lần \\ dựa trên thời gian}",
    },
    {"abbr": "2FA", "eng": "Two-Factor Authentication", "vie": "Xác thực hai yếu tố"},
    {"abbr": "MFA", "eng": "Multi-Factor Authentication", "vie": "Xác thực đa yếu tố"},
    {"abbr": "VIP", "eng": "Very Important Person", "vie": "Người rất quan trọng"},
    {"abbr": "K8s", "eng": "Kubernetes", "vie": "Công cụ quản lý container"},
    {"abbr": "CI", "eng": "Continuous Integration", "vie": "Tích hợp liên tục"},
    {
        "abbr": "CD",
        "eng": r"\makecell[l]{Continuous \\ Delivery / Deployment}",
        "vie": "Chuyển giao/Triển khai liên tục",
    },
    {
        "abbr": "LRU",
        "eng": "Least Recently Used",
        "vie": r"\makecell[l]{Thuật toán loại bỏ dữ liệu \\ ít được sử dụng gần đây nhất}",
    },
    {
        "abbr": "HTML",
        "eng": "Hyper Text Markup Language",
        "vie": "Ngôn ngữ Đánh dấu Siêu văn bản",
    },
    {
        "abbr": "TTS",
        "eng": "Text to Speech",
        "vie": "Chuyển văn bản thành giọng nói",
    },
    {
        "abbr": "STT",
        "eng": "Speech to Text",
        "vie": "Chuyển giọng nói thành văn bản",
    },
    {
        "abbr": "IaC",
        "eng": "Infrastructure as Code",
        "vie": "Cơ sở hạ tầng dưới dạng mã",
    },
    {
        "abbr": "SMTP",
        "eng": "Simple Mail Transfer Protocol",
        "vie": "Giao thức truyền thư đơn giản",
    },
    {
        "abbr": "IPN",
        "eng": "Instant Payment Notification",
        "vie": "Thông báo thanh toán tức thì",
    },
    {
        "abbr": "PSP",
        "eng": "Payment Service Provider",
        "vie": "Đơn vị cung cấp dịch vụ thanh toán",
    },
    {
        "abbr": "PSC",
        "eng": "Payment Service Consumer",
        # "vie": r"\makecell[l]{Framework Gọi thủ tục từ xa \\ do Google phát triển}",
        "vie": "Đơn vị sử dụng dịch vụ thanh toán",
    },
    {"abbr": "UI", "eng": "User Interface", "vie": "Giao diện người dùng"},
    {
        "abbr": "gRPC",
        "eng": "gRPC Remote Procedure Call",
        "vie": r"\makecell[l]{Framework Gọi thủ tục từ xa \\ do Google phát triển}",
    },
    {"abbr": "DLQ", "eng": "Dead Letter Queue", "vie": "Hàng đợi thư lỗi"},
    {"abbr": "QR Code", "eng": "Quick Response Code", "vie": "Mã phản hồi nhanh"},
    {"abbr": "TTL", "eng": "Time To Live", "vie": "Thời gian tồn tại"},
    {"abbr": "VBPL", "eng": "Văn bản pháp luật", "vie": "Văn bản pháp luật"},
    {"abbr": "DB", "eng": "Database", "vie": "Cơ sở dữ liệu"},
    # {"abbr": "HTTP", "eng": "database", "vie": "Cơ sở dữ liệu"},
    {"abbr": "DNS", "eng": "Domain Name System", "vie": "Hệ thống phân giải tên miền"},
    # {"abbr": "ID", "eng": "Identification", "vie": "Mã định danh"},
    {"abbr": "VPS", "eng": "Virtual Private Server", "vie": "Máy chủ riêng ảo"},
    {
        "abbr": "UML",
        "eng": "Unified Modeling Language",
        "vie": "Ngôn ngữ mô hình hóa thống nhất",
    },
    # {"abbr": "ADMIN", "eng": "Administrator", "vie": "Quản trị viên"},
    # {"abbr": "YAML", "eng": "YAML Ain't Markup Language", "vie": "Ngôn ngữ tuần tự hóa dữ liệu YAML"},
    # {"abbr": "RAM", "eng": "Random Access Memory", "vie": "Bộ nhớ truy cập ngẫu nhiên"},
    # {"abbr": "CPU", "eng": "Central Processing Unit", "vie": "Bộ xử lý trung tâm"},
    # {"abbr": "GPU", "eng": "Graphics Processing Unit", "vie": "Bộ xử lý đồ họa"},
    # {"abbr": "CRUD", "eng": "Create, Read, Update, Delete", "vie": "Tạo, Đọc, Cập nhật, Xóa"},
    # {"abbr": "ZIP", "eng": "ZIP Archive", "vie": "Định dạng tệp nén ZIP"},
    # {"abbr": "JSON", "eng": "JavaScript Object Notation", "vie": "Ký hiệu đối tượng JavaScript"},
    # {"abbr": "JSONL", "eng": "JSON Lines", "vie": "Định dạng JSON đa dòng"},
    # {"abbr": "URI", "eng": "Uniform Resource Identifier", "vie": "Định danh tài nguyên đồng nhất"},
    {
        "abbr": "URL",
        "eng": "Uniform Resource Locator",
        "vie": "Trình định vị tài nguyên đồng nhất",
    },
    # {"abbr": "PORT", "eng": "Port", "vie": "Cổng kết nối / Cổng giao tiếp"},
    # {"abbr": "REST", "eng": "Representational State Transfer", "vie": "Chuyển giao trạng thái đại diện"},
    {
        "abbr": "UUID",
        "eng": "Universally Unique Identifier",
        "vie": "Mã định danh duy nhất toàn cầu",
    },
    {
        "abbr": "AAL1 / AAL2",
        "eng": r"\makecell[l]{Authenticator Assurance \\ Level 1 / 2}",
        "vie": "Mức độ đảm bảo xác thực 1 / 2",
    },
    # {"abbr": "AAL2", "eng": "Authenticator Assurance Level 2", "vie": "Mức độ đảm bảo xác thực 2"}
]

# OCR	Optical Character Recognition (Công nghệ nhận dạng chữ qua ảnh)

# # Ack
# # <!-- UML -->


# # CQRS (Command Query Responsibility Segregation)

# # là mẫu thiết kế tách biệt mô hình dữ liệu cho các thao tác đọc (Query) và ghi (Command). Việc tách biệt này giúp tối ưu hóa hiệu suất, tăng khả năng mở rộng (scalability), bảo mật tốt hơn và quản lý độ phức tạp trong các hệ thống lớn

# # <!-- CQRS là viết tắt của Command and Query Responsibility Segregation -->


# \textbf{STT} & \textbf{Từ viết tắt} & \textbf{Từ viết đầy đủ} & \textbf{Mô tả} \\ \hline

# 1 & CNTT & Công nghệ thông tin & Công nghệ thông tin \\ \hline

# 2 & OOP & Object Oriented Programming & \makecell[l]{Kỹ thuật lập trình \\ hướng đối tượng} \\ \hline
# 3 & ORM & Object Relational Mapping & \makecell[l]{Kỹ thuật ánh xạ \\ các đối tượng lập trình\\ với từng bảng trong\\ cơ sở dữ liệu} \\ \hline


# 5 & DBMS & Database Management System & \makecell[l]{Hệ quản trị cơ sở dữ liệu} \\ \hline


# 9 & HMAC & Hash-based Message Authentication Code & \makecell[l]{Mã xác thực tin nhắn \\ dựa trên băm} \\ \hline


TEX_PATH = os.path.join(
    env.PATH_FOLDER_LATEX,
    "contents",
    "0",
    # "danh_sach_viet_tat",
    # "danh_sach_viet_tat.tex",
    "danh_muc",
    "DANH_MUC_KY_HIEU.tex",
)

# Số ký tự tối đa trong một dòng trước khi xuống dòng (\\)
MAX_LINE_LENGTH = 40
MAX_ENG_LINE_LENGTH = 40
MAX_VIE_LINE_LENGTH = 40


def wrap_text(text: str, max_length: int = MAX_LINE_LENGTH) -> str:
    """Tự động ngắt dòng dài thành makecell nếu vượt quá max_length ký tự."""
    if r"\makecell" in text:
        return text

    if len(text) <= max_length:
        return text

    words = text.split()
    lines = []
    current = ""

    for word in words:
        if current and len(current) + 1 + len(word) > max_length:
            lines.append(current)
            current = word
        else:
            current = (current + " " + word).strip()

    if current:
        lines.append(current)

    if len(lines) == 1:
        return lines[0]

    return r"\makecell[l]{" + r" \\ ".join(lines) + "}"


def check_duplicates():
    seen = {}
    duplicates = []
    for item in DATA:
        abbr = item["abbr"]
        if abbr in seen:
            duplicates.append(abbr)
        else:
            seen[abbr] = True
    if duplicates:
        raise ValueError(f"Duplicate abbreviations found: {', '.join(duplicates)}")


def generate_tex():
    check_duplicates()
    sorted_data = sorted(DATA, key=lambda x: x["abbr"])

    rows = []
    for i, item in enumerate(sorted_data, start=1):
        eng_cell = wrap_text(item["eng"], MAX_ENG_LINE_LENGTH)
        vie_cell = wrap_text(item["vie"], MAX_VIE_LINE_LENGTH)
        row = f"{i} & {item['abbr']} & {eng_cell} & {vie_cell} \\\\ \\hline"
        rows.append(row)

    rows_str = "\n".join(rows)

    tex_content = rf"""% DANH MỤC KÝ HIỆU

\newpage
\phantomsection
{{\centering \section*{{DANH MỤC KÝ HIỆU}}}} % Đặt tên tiêu đề
\addcontentsline{{toc}}{{section}}{{DANH MỤC KÝ HIỆU}} % Thêm vào mục lục

\begin{{table}}[ht]
\centering
\small
\begin{{tabular}}{{|c|p{{2.1cm}}|p{{4.3cm}}|p{{5.4cm}}|}}
\hline
\textbf{{STT}} & \textbf{{Từ viết tắt}} & \textbf{{Từ viết đầy đủ}} & \textbf{{Mô tả}} \\ \hline
{rows_str}
\end{{tabular}}
\end{{table}}

\newpage
"""

    os.makedirs(os.path.dirname(TEX_PATH), exist_ok=True)

    with open(TEX_PATH, "w", encoding="utf-8") as f:
        f.write(tex_content)

    print(f"Successfully updated: {TEX_PATH}")


def remove_abbreviations(file_path, data_list):
    try:
        # Bước 1: Đọc nội dung file
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()

        # Bước 2: Duyệt qua danh sách và thay thế
        for item in data_list:
            abbr = item.get("abbr")
            if abbr:
                # Tạo pattern với \b để chỉ tìm chính xác các từ đứng độc lập
                # re.escape giúp xử lý an toàn nếu trong abbr có chứa các ký tự đặc biệt
                pattern = r"\b" + re.escape(abbr) + r"\b"

                # Thay thế bằng chuỗi rỗng ""
                content = re.sub(pattern, "", content)

        # Bước 3: Ghi lại nội dung đã chỉnh sửa vào file gốc
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)

        print("Đã xóa thành công các từ viết tắt trong file!")

    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file tại đường dẫn {file_path}")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")


if __name__ == "__main__":
    generate_tex()

    # file_path = r"C:\Users\Admin\Documents\GitHub\docs-tech\x.md"

    # remove_abbreviations(file_path, DATA)
