#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import json
from typing import Any, Dict, Optional

from google.cloud import firestore
from google.oauth2 import service_account


class FirestoreWriter:
    def __init__(self, project_id: str, credentials_json: Optional[str] = None):
        connection = {}

        connection["project"] = project_id

        if credentials_json:
            try:
                json_account_info = json.loads(credentials_json)
            except ValueError:
                raise ValueError("The 'credentials_json' field must contain a valid JSON document with service account access data.")
            credentials = service_account.Credentials.from_service_account_info(json_account_info)
            connection["credentials"] = credentials

        self.client = firestore.Client(**connection)

    def check(self) -> bool:
        return bool(list(self.client.collections()))

    def write(self, stream: str, data: Dict[str, Any]) -> None:
        self.client.collection(stream).add(data)

    def purge(self, stream: str) -> None:
        for doc in self.client.collection(stream).stream():
            doc.reference.delete()
