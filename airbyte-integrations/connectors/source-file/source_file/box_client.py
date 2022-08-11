#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import requests


class BoxURLDownload:

    base_url = "https://api.box.com"

    def __init__(self, access_token: str):
        self.access_token = access_token

    def _get_box_download_endpoint(self, file_id) -> str:
        path = f"/2.0/files/{file_id}/content"
        endpoint = self.base_url + path
        return endpoint

    def get_download_url(self, shared_link: str) -> str:

        headers = {
            "Authorization": "Bearer " + self.access_token,
            "BoxApi": f"shared_link={shared_link}"
        }

        response = requests.get("https://api.box.com/2.0/shared_items", headers=headers)
        response_json = response.json()
        assert response_json['type'] == 'file'
        file_id = response_json['id']
        url = self._get_box_download_endpoint(file_id)

        response = requests.get(url, headers=headers, allow_redirects=False)
        return response.headers["location"]
