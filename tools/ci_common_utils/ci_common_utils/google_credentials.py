import time
from dataclasses import dataclass
from typing import Mapping, Any, List, ClassVar, Tuple, Optional

import jwt
import requests

from .logger import Logger

TOKEN_TTL = 3600


@dataclass
class GoogleApi:
    logger: ClassVar[Logger] = Logger()

    config: Mapping[str, Any]
    scopes: List[str]
    _access_token: str = None

    def get(self, url: str) -> Tuple[Mapping[str, Any], Optional[str]]:
        token = self.get_access_token()
        return None, "sss"

    @property
    def token_uri(self):
        return self.config["token_uri"]

    def __generate_jwt(self) -> str:
        """Generate JWT token by a service account json file and scopes"""
        now = int(time.time())
        claim = {
            "iat": now,
            "iss": self.config["client_email"],
            "scope": ",".join(self.scopes),
            "aud": self.token_uri,
            "exp": now + TOKEN_TTL,
        }
        return jwt.encode(claim, self.config["private_key"].encode(), algorithm="RS256")

    def get_access_token(self):
        """Generates an access token by a service account json file and scopes"""

        if self._access_token is None:
            self._access_token = self.__get_access_token()

        return self._access_token

    def __get_access_token(self) -> str:
        jwt = self.__generate_jwt()
        resp = requests.post(self.token_uri, data={
            "assertion": jwt,
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        })
        return resp.json()["access_token"], None

# "${config_file}" "$scopes"
# `
# local
# token_uri =$(_parse_token_uri "${config_file}")
# local
# data =$(curl - s - X POST ${token_uri} \
#     --data-urlencode "assertion=${jwt}" \
#     --data-urlencode 'grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer'
#         )
# echo $data | jq - r.access_token
# }

# !/usr/bin/env bash
# Test script to access/generate secrets in Secret Manager

# PROJECT="engineering-devops"
# SCOPE="https://www.googleapis.com/auth/cloud-platform"
# SERVICE_ACCOUNT_FILE=secret-manager.json
# SECRET=my-secret
# TOKEN_TTL = 3600
#
# _var2base64()
# {
#     printf
# "$1" | _urlencode_base64
# }
#
# _urlencode_base64()
# {
#     base64 | tr
# '/+' '_-' | tr - d
# '=\n'
# }
#
# function
# _parse_token_uri()
# {
#     local
# config_file =$1
# local
# token_uri =$(jq - r.token_uri ${config_file})
# echo
# "${token_uri}"
# }
#
# function

#
# function
# parse_project_id()
# {
#     # find a project_id into config file
#     local
# config_file =$1
# local
# project_id =$(jq - r.project_id ${config_file})
# echo
# "${project_id}"
# }
#
