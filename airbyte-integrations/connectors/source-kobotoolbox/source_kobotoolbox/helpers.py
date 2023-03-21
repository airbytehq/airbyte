#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


class Helpers(object):
    @staticmethod
    def get_json_schema():
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {"_id": {"type": "string"}, "indexed_on": {"type": "string", "format": "date-time"}},
        }
        return json_schema
