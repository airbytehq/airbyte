#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json

import yaml

# Use the libYAML versions if possible
try:
    from yaml import CDumper as Dumper
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Dumper, Loader


class VcrHelper:
    def __init__(self, path_to_test_fixture):
        with open(path_to_test_fixture, "r") as f:
            self.test_fixture = json.loads(f.read())

    def get_filter_headers(self):
        return self._get_filters("filter_headers")

    def get_filters(self):
        return {field: self._get_filters(field) for field in ["filter_headers"]}

    def _get_filters(self, field):
        return [(fh["name"], fh.get("value")) for fh in self.test_fixture[field]]

    def deserialize(self, cassette_string):
        return yaml.load(cassette_string, Loader=Loader)

    def serialize(self, cassette_dict):
        serialized = yaml.dump(cassette_dict, Dumper=Dumper)
        for replace in self.test_fixture["replace_all"]:
            original = replace["original"]
            replace_by = replace["replace_by"]
            serialized = serialized.replace(original, replace_by)
        return serialized
