#
# Copyright (c) 2025 Airbyte, Inc., all rights reserved.
#

import base64
import hashlib
import hmac as hmac_lib
import json
import re
from typing import Any, Dict, Optional


def hash(value: Any, hash_type: str = "md5", salt: Optional[str] = None) -> str:
    """
      Implementation of a custom Jinja2 hash filter
      Hash type defaults to 'md5' if one is not specified.

      If you are using this has function for GDPR compliance, then
      you should probably also pass in a salt as discussed in:
      https://security.stackexchange.com/questions/202022/hashing-email-addresses-for-gdpr-compliance

      This can be used in a low code connector definition under the AddFields transformation.
      For example:

    rates_stream:
      $ref: "#/definitions/base_stream"
      $parameters:
        name: "rates"
        primary_key: "date"
        path: "/exchangerates_data/latest"
      transformations:
        - type: AddFields
          fields:
            - path: ["some_new_path"]
              value: "{{ record['rates']['CAD'] | hash('md5', 'mysalt')  }}"



      :param value: value to be hashed
      :param hash_type: valid hash type
      :param salt: a salt that will be combined with the value to ensure that the hash created for a given value on this system
                   is different from the hash created for that value on other systems.
      :return: computed hash as a hexadecimal string
    """
    hash_func = getattr(hashlib, hash_type, None)

    if hash_func:
        hash_obj = hash_func()
        hash_obj.update(str(value).encode("utf-8"))
        if salt:
            hash_obj.update(str(salt).encode("utf-8"))
        computed_hash: str = hash_obj.hexdigest()
    else:
        raise AttributeError("No hashing function named {hname}".format(hname=hash_type))

    return computed_hash


def base64encode(value: str) -> str:
    """
    Implementation of a custom Jinja2 base64encode filter

    For example:

      OAuthAuthenticator:
        $ref: "#/definitions/OAuthAuthenticator"
        $parameters:
          name: "client_id"
          value: "{{ config['client_id'] | base64encode }}"

    :param value: value to be encoded in base64
    :return: base64 encoded string
    """

    return base64.b64encode(value.encode("utf-8")).decode()


def base64decode(value: str) -> str:
    """
    Implementation of a custom Jinja2 base64decode filter

    For example:

      OAuthAuthenticator:
        $ref: "#/definitions/OAuthAuthenticator"
        $parameters:
          name: "client_id"
          value: "{{ config['client_id'] | base64decode }}"

    :param value: value to be decoded from base64
    :return: base64 decoded string
    """

    return base64.b64decode(value.encode("utf-8")).decode()


def base64binascii_decode(value: str) -> str:
    """
    Implementation of a custom Jinja2 filter to decode base64 strings using ASCII encoding

    For example:

      OAuthAuthenticator:
        $ref: "#/definitions/OAuthAuthenticator"
        $parameters:
          name: "client_id"
          value: "{{ config['client_id'] | base64binascii_decode }}"

    :param value: value to be decoded from base64 using ascii
    :return: base64 decoded string ascii
    """
    return base64.standard_b64encode(value.encode("ascii")).decode("ascii")


def string(value: Any) -> str:
    """
    Converts the input value to a string.
    If the value is already a string, it is returned as is.
    Otherwise, the value is interpreted as a json object and wrapped in triple-quotes so it's evalued as a string by the JinjaInterpolation
    :param value: the value to convert to a string
    :return: string representation of the input value
    """
    if isinstance(value, str):
        return value
    ret = f'"""{json.dumps(value)}"""'
    return ret


def regex_search(value: str, regex: str) -> str:
    """
    Match a regular expression against a string and return the first match group if it exists.
    """
    match = re.search(regex, value)
    if match and len(match.groups()) > 0:
        return match.group(1)
    return ""


def hmac(value: Any, key: str, hash_type: str = "sha256") -> str:
    """
    Implementation of a custom Jinja2 hmac filter with SHA-256 support.

    This filter creates a Hash-based Message Authentication Code (HMAC) using a cryptographic
    hash function and a secret key. Currently only supports SHA-256, and returns hexdigest of the signature.

    Example usage in a low code connector:

    auth_headers:
      $ref: "#/definitions/base_auth"
      $parameters:
        signature: "{{ 'message_to_sign' | hmac('my_secret_key') }}"

    :param value: The message to be authenticated
    :param key: The secret key for the HMAC
    :param hash_type: Hash algorithm to use (default: sha256)
    :return: HMAC digest as a hexadecimal string
    """
    # Define allowed hash functions
    ALLOWED_HASH_TYPES: Dict[str, Any] = {
        "sha256": hashlib.sha256,
    }

    if hash_type not in ALLOWED_HASH_TYPES:
        raise ValueError(
            f"Hash type '{hash_type}' is not allowed. Allowed types: {', '.join(ALLOWED_HASH_TYPES.keys())}"
        )

    hmac_obj = hmac_lib.new(
        key=str(key).encode("utf-8"),
        msg=str(value).encode("utf-8"),
        digestmod=ALLOWED_HASH_TYPES[hash_type],
    )

    return hmac_obj.hexdigest()


_filters_list = [
    hash,
    base64encode,
    base64decode,
    base64binascii_decode,
    string,
    regex_search,
    hmac,
]
filters = {f.__name__: f for f in _filters_list}
