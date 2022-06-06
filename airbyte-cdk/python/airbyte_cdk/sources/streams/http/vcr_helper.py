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
        # cassette_string = cassette_string.replace("", "faketoken")
        print(f"replace_all: {self.test_fixture['replace_all']}")
        for replace in self.test_fixture["replace_all"]:
            original = replace["original"]
            replace_by = replace["replace_by"]
            cassette_string = cassette_string.replace(original, replace_by)
        return yaml.load(cassette_string, Loader=Loader)

    def serialize(self, cassette_dict):
        return yaml.dump(cassette_dict, Dumper=Dumper)
