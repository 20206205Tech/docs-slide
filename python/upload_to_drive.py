import json
import os
from datetime import datetime

import pytz
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ID thư mục Google Drive bạn đã cung cấp
GOOGLE_DRIVE_FOLDER_ID = "1GVo-Vus0E2b4_SKf3XoYZd9mZA5oqE8U"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# Đường dẫn tới file PDF (từ thư mục python/ trỏ ngược ra thư mục latex/)
PDF_LOCAL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "latex", "VuVanNghia-20206205.pdf"
)


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

    # Tạo tên file mới có kèm thời gian
    time_suffix = get_hanoi_time()
    new_file_name = f"VuVanNghia-20206205_{time_suffix}.pdf"

    print(f"🚀 Đang tải file lên với tên: {new_file_name}")

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
