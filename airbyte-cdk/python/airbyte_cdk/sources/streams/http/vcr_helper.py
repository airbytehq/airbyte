#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#
import json


class VcrHelper:
    def __init__(self, path_to_test_fixture):
        with open(path_to_test_fixture, "r") as f:
            self.test_fixture = json.loads(f.read())

    def get_filter_headers(self):
        return self._get_filters("filter_headers")

    def get_filters(self):
        return {field: self._get_filters(field) for field in ["filter_headers"]}

    def _get_filters(self, field):
        return [(fh["name"], fh.get("value", None)) for fh in self.test_fixture[field]]
