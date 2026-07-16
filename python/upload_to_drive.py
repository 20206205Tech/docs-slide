import json
import mimetypes
import os
from datetime import datetime
from pathlib import Path

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

PROJECT_DIR = Path(__file__).resolve().parents[1]


def get_upload_file_info():
    """Lấy đường dẫn, tên file gốc, và mimetype cần upload."""
    local_file_path = os.environ.get("LOCAL_FILE_PATH")

    if local_file_path:
        upload_path = Path(local_file_path)

        if not upload_path.is_absolute():
            upload_path = PROJECT_DIR / upload_path

        drive_file_name = os.environ.get("DRIVE_FILE_NAME", upload_path.name)
    else:
        upload_path = PROJECT_DIR / "latex" / PDF_FILE_NAME
        drive_file_name = os.environ.get("DRIVE_FILE_NAME", PDF_FILE_NAME)

    mime_type = os.environ.get("MIME_TYPE")

    if not mime_type:
        mime_type = (
            mimetypes.guess_type(upload_path.name)[0] or "application/octet-stream"
        )

    return upload_path, drive_file_name, mime_type


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
    upload_path, drive_file_name, mime_type = get_upload_file_info()

    if not upload_path.exists():
        print(f"❌ Không tìm thấy file tại: {upload_path}")
        print("Vui lòng đảm bảo file đã được tạo trước khi upload.")
        return

    print("🔑 Đang xác thực Google Drive...")
    service = get_drive_service()

    # Tạo tên file mới có kèm thời gian.
    time_suffix = get_hanoi_time()
    file_stem = Path(drive_file_name).stem
    file_suffix = Path(drive_file_name).suffix
    new_file_name = f"{file_stem}_{time_suffix}{file_suffix}"

    print(
        f"🚀 Đang tải file lên thư mục ID [{GOOGLE_DRIVE_FOLDER_ID}] với tên: {new_file_name}"
    )

    file_metadata = {"name": new_file_name, "parents": [GOOGLE_DRIVE_FOLDER_ID]}

    media = MediaFileUpload(str(upload_path), mimetype=mime_type, resumable=True)

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
