#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import base64
from dataclasses import dataclass

from airbyte_cdk.sources.declarative.auth.token import BasicHttpAuthenticator


@dataclass
class CustomAuthenticator(BasicHttpAuthenticator):
    @property
    def token(self):
        username = self._username.eval(self.config).encode("latin1")
        password = self._password.eval(self.config).encode("latin1")
        encoded_credentials = base64.b64encode(b":".join((username, password))).strip()
        token = "Basic " + encoded_credentials.decode("utf-8")
        return token
