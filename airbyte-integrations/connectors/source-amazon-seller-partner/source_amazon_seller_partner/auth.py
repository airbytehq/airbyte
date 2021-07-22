#
# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from __future__ import print_function

import datetime
import hashlib
import hmac
import logging
import urllib.parse
from collections import OrderedDict

from requests.auth import AuthBase
from requests.compat import urlparse

log = logging.getLogger(__name__)


def sign_msg(key, msg):
    """ Sign message using key """
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()


class AWSSigV4(AuthBase):
    def __init__(self, service, **kwargs):
        self.service = service
        self.aws_access_key_id = kwargs.get("aws_access_key_id")
        self.aws_secret_access_key = kwargs.get("aws_secret_access_key")
        self.aws_session_token = kwargs.get("aws_session_token")
        if self.aws_access_key_id is None or self.aws_secret_access_key is None:
            raise KeyError("AWS Access Key ID and Secret Access Key are required")
        self.region = kwargs.get("region")

    def __call__(self, r):
        t = datetime.datetime.utcnow()
        self.amzdate = t.strftime("%Y%m%dT%H%M%SZ")
        self.datestamp = t.strftime("%Y%m%d")
        log.debug("Starting authentication with amzdate=%s", self.amzdate)
        p = urlparse(r.url)

        host = p.hostname
        uri = urllib.parse.quote(p.path)

        # sort query parameters alphabetically
        if len(p.query) > 0:
            split_query_parameters = list(map(lambda param: param.split("="), p.query.split("&")))
            ordered_query_parameters = sorted(split_query_parameters, key=lambda param: (param[0], param[1]))
        else:
            ordered_query_parameters = list()

        canonical_querystring = "&".join(map(lambda param: "=".join(param), ordered_query_parameters))

        headers_to_sign = {"host": host, "x-amz-date": self.amzdate}
        if self.aws_session_token is not None:
            headers_to_sign["x-amz-security-token"] = self.aws_session_token

        ordered_headers = OrderedDict(sorted(headers_to_sign.items(), key=lambda t: t[0]))
        canonical_headers = "".join(map(lambda h: ":".join(h) + "\n", ordered_headers.items()))
        signed_headers = ";".join(ordered_headers.keys())

        if r.method == "GET":
            payload_hash = hashlib.sha256("".encode("utf-8")).hexdigest()
        else:
            if r.body:
                payload_hash = hashlib.sha256(r.body.encode("utf-8")).hexdigest()
            else:
                payload_hash = hashlib.sha256("".encode("utf-8")).hexdigest()

        canonical_request = "\n".join([r.method, uri, canonical_querystring, canonical_headers, signed_headers, payload_hash])

        credential_scope = "/".join([self.datestamp, self.region, self.service, "aws4_request"])
        string_to_sign = "\n".join(
            ["AWS4-HMAC-SHA256", self.amzdate, credential_scope, hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()]
        )
        log.debug("String-to-Sign: '%s'", string_to_sign)

        kDate = sign_msg(("AWS4" + self.aws_secret_access_key).encode("utf-8"), self.datestamp)
        kRegion = sign_msg(kDate, self.region)
        kService = sign_msg(kRegion, self.service)
        kSigning = sign_msg(kService, "aws4_request")
        signature = hmac.new(kSigning, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

        authorization_header = "AWS4-HMAC-SHA256 Credential={}/{}, SignedHeaders={}, Signature={}".format(
            self.aws_access_key_id, credential_scope, signed_headers, signature
        )
        r.headers.update(
            {
                "host": host,
                "x-amz-date": self.amzdate,
                "Authorization": authorization_header,
                "x-amz-security-token": self.aws_session_token,
            }
        )
        return r
