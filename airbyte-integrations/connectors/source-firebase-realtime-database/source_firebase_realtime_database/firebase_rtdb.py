#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json

import firebase_admin
from firebase_admin import credentials, db


class Client:
    def __init__(self, path="", buffer_size=10000):
        self._path = path
        self._buffer_size = buffer_size

    def initialize(self, database_name, google_application_credentials):
        database_url = f"https://{database_name}.firebaseio.com"
        sa_key = json.loads(google_application_credentials)

        cred = credentials.Certificate(sa_key)

        firebase_admin.initialize_app(
            cred,
            {
                "databaseURL": database_url,
            },
        )
        self._ref = db.reference(self._path)

    def check_connection(self):
        self._ref.get(shallow=True)

    def fetch_records(self, start_key=None):
        if start_key:
            return self._ref.order_by_key().start_at(start_key).limit_to_first(self._buffer_size).get()
        else:
            return self._ref.order_by_key().limit_to_first(self._buffer_size).get()

    def extract(self):
        return Records(self)

    def set_records(self, records):
        self._ref.set(records)

    def delete_records(self):
        self._ref.delete()


class Records:
    def __init__(self, client):
        self._client = client

    def __iter__(self):
        def _gen():
            records = self._client.fetch_records()
            if records is None or len(records) == 0:
                return

            for k, v in records.items():
                last_key = k
                data = {"key": k, "value": json.dumps(v)}

                yield data

            # fetch data start at last_key inclusive
            while records := self._client.fetch_records(last_key):
                num_records = len(records)

                records_iter = iter(records.items())
                first_key, first_value = next(records_iter)
                if first_key == last_key:
                    if num_records == 1:
                        return
                else:
                    last_key = first_key
                    data = {"key": first_key, "value": json.dumps(first_value)}
                    yield data

                for k, v in records_iter:
                    last_key = k
                    data = {"key": k, "value": json.dumps(v)}

                    yield data

        return _gen()
