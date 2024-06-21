import json
import base64
import pendulum
import requests

from urllib.parse import urlparse, quote, urlencode
from typing import Any, Mapping

from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

from requests.auth import AuthBase


date_time_fmt = "%Y-%m-%dT%H:%M:%SZ"


# Generate signature and sign a request
def RSA_sign(data, privateKey):
    private_keyBytes = base64.b64decode(privateKey)
    priKey = RSA.importKey(private_keyBytes)
    signer = PKCS1_v1_5.new(priKey)
    hash_obj = SHA256.new(data.encode("utf-8"))
    signature = base64.b64encode(signer.sign(hash_obj))
    return signature


def sign(httpMethod, uriWithQueryString, clientId, timeString, reqBody):
    reqContent = httpMethod + " " + uriWithQueryString + "\n" + clientId + "." + timeString + "." + reqBody
    return reqContent


def get_authorization_header_str(method: str, path: str, client_id: str, private_key: str, date_time: str, body: str) -> str:

    NAME_VALUE_SEPARATOR = "="
    COMMA = ","
    ALGORITHM = "algorithm"
    SIGNATURE = "signature"
    KEY_VERSION = "keyVersion"
    RSA_256 = "RSA256"
    uri = quote(path)
    sign_data = sign(method, uri, client_id, date_time, body)
    res_sign1 = RSA_sign(sign_data, private_key)
    signature = res_sign1.decode("utf-8")
    values = {}
    values["signature"] = signature
    data = urlencode(values)
    res = ALGORITHM + NAME_VALUE_SEPARATOR + RSA_256 + COMMA + KEY_VERSION + NAME_VALUE_SEPARATOR + "1" + COMMA + data

    return res


class RSA256_Signature(AuthBase):

    def __init__(self, client_id: str, private_key: str, base_url: str):
        self.client_id = client_id
        self.private_key = private_key
        self.base_url = base_url

    def get_auth_header(self):
        return {
            "Content-Type": "Content-Type: application/json; charset=UTF-8",
            "Client-Id": self.client_id,
        }
    
    def __call__(self, prepared_request: requests.PreparedRequest) -> requests.PreparedRequest:

        req_body = prepared_request.body
        str1=str(prepared_request.body, encoding = "utf-8")  

        body_str = str(json.dumps(json.loads(str1), separators=(",", ":")))
        # rebuilt body
        prepared_request.prepare_body(data=body_str,files=None)
        current_ts = pendulum.now("utc")
        date_time = current_ts.strftime(date_time_fmt)
        self.request_time = date_time
        url_parsed = urlparse(prepared_request.url)
        uri = quote(url_parsed.path)

        sign_str = get_authorization_header_str(prepared_request.method, uri, self.client_id, self.private_key, date_time, body_str)
        prepared_request.headers.update(
            {
                "Content-Type": "Content-Type: application/json; charset=UTF-8",
                "Signature": sign_str,
                "Request-Time": date_time,
                "Client-Id": self.client_id,
            }
        )
        return prepared_request


