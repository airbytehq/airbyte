# Copyright (c) 2023 Airbyte, Inc., all rights reserved.


from urllib.parse import urlparse


def get_folder_id(url_string: str) -> str:
    """
    Extract the folder ID from a Google Drive folder URL.

    Takes the last path segment of the URL, which is the folder ID (ignoring trailing slashes and query parameters).
    """
    try:
        parsed_url = urlparse(url_string)
        if parsed_url.scheme != "https" or parsed_url.netloc != "drive.google.com":
            raise ValueError("Folder URL has to be of the form https://drive.google.com/drive/folders/<folder_id>")
        path_segments = list(filter(None, parsed_url.path.split("/")))
        if path_segments[-2] != "folders" or len(path_segments) < 3:
            raise ValueError("Folder URL has to be of the form https://drive.google.com/drive/folders/<folder_id>")
        return path_segments[-1]
    except Exception:
        raise ValueError("Folder URL is invalid")
