#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#


class Helpers(object):
    @staticmethod
    def get_json_schema():
        json_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "properties": {
                "_id": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
                "formhub/uuid": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
                "starttime": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
                "__version__": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
                "meta/instanceID": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
                "_xform_id_string": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
                "_uuid": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
                "_attachments": {
                    "type": [
                        "array",
                        "null"
                    ]
                },
                "_status": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
                "_geolocation": {
                    "type": [
                        "array",
                        "null"
                    ]
                },
                "_tags": {
                    "type": [
                        "array",
                        "null"
                    ]
                },
                "_notes": {
                    "type": [
                        "array",
                        "null"
                    ]
                },
                "_validation_status": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
                "_submission_time": {
                    "type": [
                        "string",
                        "null"
                    ]
                },
                "_submitted_by": {
                    "type": [
                        "string",
                        "null"
                    ]
                }
            }
        }
        return json_schema
