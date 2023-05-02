import os
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from config import config, configure_logging

configure_logging(config())

GOOGLE_CREDENTIAL_FILE = "google_credential.json"
SCOPES = ["https://www.googleapis.com/auth/drive"]
FOLDER_ID = "1xpclxjzEgp2Im5383ylHSD_K3H4-uOrz"
WORD_FOLDER = "data/src_words"


def get_files(query):
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_CREDENTIAL_FILE, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=credentials)
    results = (
        service.files()  # pylint: disable=no-member
        .list(q=query, pageSize=100, fields="files(id, name, mimeType)")
        .execute()
    )
    items = results.get("files", [])
    return items


def download_file(file_id, file_name):
    credentials = service_account.Credentials.from_service_account_file(
        GOOGLE_CREDENTIAL_FILE, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=credentials)
    request = service.files().get_media(fileId=file_id)  # pylint: disable=no-member
    with open(file_name, "wb") as f:
        downloader = MediaIoBaseDownload(f, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            logging.info("Download %s %d%%.", file_name, int(status.progress() * 100))


def main():
    folders = get_files(
        f"'{FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
    )
    for folder in folders:
        new_folder_path = os.path.join(WORD_FOLDER, folder["name"])
        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)
        logging.info("%s (%s)", folder["name"], folder["id"])
        query = (
            f"'{folder['id']}' in parents and "
            f"(mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document') and "
            f"trashed=false"
        )
        text_files = get_files(
            query=query,
        )
        for text_file in text_files:
            logging.info(" - %s (%s)", text_file["name"], text_file["id"])
            download_file(
                text_file["id"], os.path.join(new_folder_path, text_file["name"])
            )


if __name__ == "__main__":
    main()
