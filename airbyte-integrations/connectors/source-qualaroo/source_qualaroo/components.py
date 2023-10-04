#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import requests
from typing import Any, List, Mapping
from base64 import b64encode
from dataclasses import dataclass
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

        extracted=[]
        for rec in response.json():
            if "answered_questions" in rec:
                rec["answered_questions"] = list(rec["answered_questions"].values())
            extracted.append(rec)
        return extracted
