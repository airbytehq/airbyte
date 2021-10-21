#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

import json;
from google.cloud import firestore
from google.oauth2 import service_account

class FirestoreWriter:
    def __init__(self, project_id=None, credentials_json=None, collection=None):
        connection = {}

        if project_id:
            connection['project'] =project_id

        if credentials_json:
            json_account_info = json.loads(credentials_json)
            credentials = service_account.Credentials.from_service_account_info(
            json_account_info)
            connection['credentials'] = credentials

        self.client = firestore.Client(**connection)

    def check(self):
        return bool(list(self.client.collections()))

    def write(self, stream, data):
        self.client.collection(stream).add(data)

    def purge(self, stream):
        for doc in self.client.collection(stream).stream():
            doc.reference.delete()
