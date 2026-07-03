import json
import os
from datetime import datetime

import pytz
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Mặc định (bản Prod), nếu có biến môi trường truyền từ GitHub Actions thì sẽ lấy giá trị đó
GOOGLE_DRIVE_FOLDER_ID = os.environ.get(
    "DRIVE_FOLDER_ID", "1TbMNTUkGjA3EUbt-8BYMx2oDWkntDqXM"
)
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# Lấy tên file động từ biến môi trường (mặc định là bản chính thức)
PDF_FILE_NAME = os.environ.get("PDF_FILE_NAME", "VuVanNghia-20206205.pdf")

# Đường dẫn tới file PDF
PDF_LOCAL_PATH = os.path.join(os.path.dirname(__file__), "..", "latex", PDF_FILE_NAME)


def get_hanoi_time(format_str="%d-%m-%Y_%H-%M-%S"):
    """Lấy thời gian hiện tại theo múi giờ Hà Nội."""
    hanoi_tz = pytz.timezone("Asia/Ho_Chi_Minh")
    now_hanoi = datetime.now(hanoi_tz)
    return now_hanoi.strftime(format_str)


def get_drive_service():
    """Khởi tạo và xác thực API Google Drive từ biến môi trường"""
    token_json = os.environ.get("GOOGLE_DRIVE_TOKEN")
    if not token_json:
        raise Exception("❌ Không tìm thấy biến môi trường GOOGLE_DRIVE_TOKEN!")

    creds_info = json.loads(token_json)
    creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
    return build("drive", "v3", credentials=creds)


def main():
    if not os.path.exists(PDF_LOCAL_PATH):
        print(f"❌ Không tìm thấy file PDF tại: {PDF_LOCAL_PATH}")
        print("Vui lòng đảm bảo bạn đã biên dịch LaTeX thành công.")
        return

    print("🔑 Đang xác thực Google Drive...")
    service = get_drive_service()

    # Tạo tên file mới có kèm thời gian và giữ nguyên tiền tố dev (nếu có)
    time_suffix = get_hanoi_time()

    if PDF_FILE_NAME.startswith("dev-"):
        new_file_name = f"dev-VuVanNghia-20206205_{time_suffix}.pdf"
    else:
        new_file_name = f"VuVanNghia-20206205_{time_suffix}.pdf"

    print(
        f"🚀 Đang tải file lên thư mục ID [{GOOGLE_DRIVE_FOLDER_ID}] với tên: {new_file_name}"
    )

    file_metadata = {"name": new_file_name, "parents": [GOOGLE_DRIVE_FOLDER_ID]}

    media = MediaFileUpload(PDF_LOCAL_PATH, mimetype="application/pdf", resumable=True)

    try:
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        file_id = file.get("id")
        print(f"✅ Tải lên thành công!")
        print(f"📄 File ID: {file_id}")
        print(
            f"🔗 Link thư mục: https://drive.google.com/drive/folders/{GOOGLE_DRIVE_FOLDER_ID}"
        )
    except Exception as e:
        print(f"❌ Lỗi khi tải file lên Drive: {e}")


if __name__ == "__main__":
    main()
