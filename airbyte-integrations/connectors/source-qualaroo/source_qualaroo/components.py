#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from base64 import b64encode
from dataclasses import dataclass
from typing import Any, List, Mapping

import requests
from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator
from airbyte_cdk.sources.declarative.extractors.record_extractor import RecordExtractor


@dataclass
class CustomAuthenticator(BasicHttpAuthenticator):
    @property
    def token(self):

        key = str(self._username.eval(self.config)).encode("latin1")
        token = self._password.eval(self.config).encode("latin1")
        encoded_credentials = b64encode(b":".join((key, token))).strip()
        token = "Basic " + encoded_credentials.decode("ascii")
        return token


class CustomExtractor(RecordExtractor):
    def extract_records(self, response: requests.Response, **kwargs) -> List[Mapping[str, Any]]:

        extracted = []
        for record in response.json():
            if "answered_questions" in record:
                record["answered_questions"] = list(record["answered_questions"].values())
            extracted.append(record)
        return extracted
