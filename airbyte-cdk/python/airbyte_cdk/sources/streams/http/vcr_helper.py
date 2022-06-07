#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json

import yaml
from airbyte_cdk.utils.airbyte_secrets_utils import filter_secrets

# Use the libYAML versions if possible
try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader

import vcr


class VcrHelper:
    def __init__(self, path_to_test_fixture=None):
        if path_to_test_fixture is not None:
            with open(path_to_test_fixture, "r") as f:
                self.test_fixture = json.loads(f.read())
        else:
            self.test_fixture = {"filter_headers": [{"name": "Authorization", "value": "<AUTHORIZATION_TOKEN_XXXX>"}]}

    def get_vcr(self):
        my_vcr = vcr.VCR()
        my_vcr.register_serializer("no_secrets", self)
        return my_vcr

    def get_filters(self, auth_header_keys):
        all_filters = {field: self._get_filters(field) for field in self.test_fixture}

        header_filters = all_filters["filter_headers"]
        headers_to_filter = [h[0] for h in header_filters]
        missing_filters = set(auth_header_keys) - set(headers_to_filter)

        for f in missing_filters:
            header_filters.append((f, "X#X#X"))
        return all_filters

    def _get_filters(self, field):
        return [(fh["name"], fh.get("value")) for fh in self.test_fixture[field]]

    def deserialize(self, cassette_string):
        return yaml.load(cassette_string, Loader=Loader)

    def serialize(self, cassette_dict):
        serialized = yaml.dump(cassette_dict, Dumper=Dumper)
        serialized = filter_secrets(serialized)
        return serialized
