#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from urllib.parse import urlparse

import requests

HTTP_STATUS_302 = 302
HTTP_STATUS_400 = 400
HTTP_STATUS_403 = 403
HTTP_STATUS_404 = 404


class NotSuccessfullyGetDownloadURLException(Exception):
    pass


class BoxFileNotFoundException(Exception):
    pass


class BoxFileAccessDeniedException(Exception):
    pass


class BoxClientException(Exception):
    pass


def exception_manager(status_code: int) -> object or None:
    return {
        HTTP_STATUS_400: BoxClientException,
        HTTP_STATUS_403: BoxFileAccessDeniedException,
        HTTP_STATUS_404: BoxFileNotFoundException,
    }.get(status_code)


class BoxURLDownload:
    """
    This class is used to issue a URL link
    to the object located in BOX Cloud
    ---
    Since BOX does not output a URL link for direct file download, this class is required

    """

    def __init__(self, raw_url: str, developer_access_token: str):
        self.box_base_url = "https://api.box.com"
        self.raw_url = raw_url
        self.developer_access_token = developer_access_token

    @property
    def _prepare_file_id_from_link(self) -> str:
        expected_file_id = urlparse(self.raw_url).path.split("/")[-1]
        return expected_file_id

    def _get_box_download_endpoint(self, file_id) -> str:
        path = f"/2.0/files/{file_id}/content"
        endpoint = self.box_base_url + path
        return endpoint

    def get_download_url(self) -> str:
        """
        Method for get Download resource URL from BOX Cloud
        """
        parsed_file_id = self._prepare_file_id_from_link
        url = self._get_box_download_endpoint(file_id=parsed_file_id)
        headers = {"Authorization": "Bearer {0}".format(self.developer_access_token)}

        response = requests.get(url=url, headers=headers, allow_redirects=False)
        if response.status_code != HTTP_STATUS_302:
            exc = exception_manager(status_code=response.status_code)
            if not exc:
                raise NotSuccessfullyGetDownloadURLException(f"{response.content}: status - {response.status_code}")
            raise exc(f"{response.content}: status - {response.status_code}")

        download_url = response.headers["location"]
        return download_url
