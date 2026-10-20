# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from urllib.parse import parse_qs, urlparse


FOLDER_URL_ERROR = (
    "Folder URL is invalid. Paste the folder link from Google Drive, for example https://drive.google.com/drive/folders/<folder-id>."
)


def get_folder_id(url_string: str) -> str:
    """
    Extract a folder ID from a Google Drive folder link.

    Supports folder links with or without a scheme, folder URLs, and the open and folderview URL formats.
    """
    url_string = url_string.strip()
    if "://" not in url_string:
        url_string = f"https://{url_string}"

    try:
        parsed_url = urlparse(url_string)
    except ValueError:
        raise ValueError(FOLDER_URL_ERROR) from None

    if parsed_url.scheme not in ("http", "https") or parsed_url.netloc != "drive.google.com":
        raise ValueError(FOLDER_URL_ERROR)

    path_segments = [segment for segment in parsed_url.path.split("/") if segment]
    if not path_segments:
        raise ValueError(FOLDER_URL_ERROR)

    last_segment = path_segments[-1]
    if last_segment in ("my-drive", "home"):
        return "root"

    if last_segment in ("open", "folderview"):
        folder_ids = parse_qs(parsed_url.query).get("id")
        if folder_ids and folder_ids[0]:
            return folder_ids[0]
        raise ValueError(FOLDER_URL_ERROR)

    if len(path_segments) >= 2 and path_segments[-2] == "folders":
        return last_segment

    raise ValueError(FOLDER_URL_ERROR)
