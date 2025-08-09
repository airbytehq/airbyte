# Copyright (c) 2024 Airbyte, Inc., all rights reserved.

import json
from typing import Dict


def get_generic_json_schema() -> Dict:
    generic_schema = """
        {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "type": {
            "type": "string"
            },
            "id": {
            "type": "string"
            },
            "file_version": {
            "type": "object",
            "properties": {
                "type": {
                "type": "string"
                },
                "id": {
                "type": "string"
                },
                "sha1": {
                "type": "string"
                }
            },
            "required": ["type", "id", "sha1"]
            },
            "sequence_id": {
            "type": "string"
            },
            "etag": {
            "type": "string"
            },
            "sha1": {
            "type": "string"
            },
            "name": {
            "type": "string"
            },
            "description": {
            "type": "string"
            },
            "size": {
            "type": "integer"
            },
            "path_collection": {
            "type": "object",
            "properties": {
                "total_count": {
                "type": "integer"
                },
                "entries": {
                "type": "array",
                "items": [
                    {
                    "type": "object",
                    "properties": {
                        "type": {
                        "type": "string"
                        },
                        "id": {
                        "type": "string"
                        },
                        "sequence_id": {
                        "type": "null"
                        },
                        "etag": {
                        "type": "null"
                        },
                        "name": {
                        "type": "string"
                        }
                    },
                    "required": ["type", "id", "sequence_id", "etag", "name"]
                    },
                    {
                    "type": "object",
                    "properties": {
                        "type": {
                        "type": "string"
                        },
                        "id": {
                        "type": "string"
                        },
                        "sequence_id": {
                        "type": "string"
                        },
                        "etag": {
                        "type": "string"
                        },
                        "name": {
                        "type": "string"
                        }
                    },
                    "required": ["type", "id", "sequence_id", "etag", "name"]
                    },
                    {
                    "type": "object",
                    "properties": {
                        "type": {
                        "type": "string"
                        },
                        "id": {
                        "type": "string"
                        },
                        "sequence_id": {
                        "type": "string"
                        },
                        "etag": {
                        "type": "string"
                        },
                        "name": {
                        "type": "string"
                        }
                    },
                    "required": ["type", "id", "sequence_id", "etag", "name"]
                    }
                ]
                }
            },
            "required": ["total_count", "entries"]
            },
            "created_at": {
            "type": "string"
            },
            "modified_at": {
            "type": "string"
            },
            "trashed_at": {
            "type": "null"
            },
            "purged_at": {
            "type": "null"
            },
            "content_created_at": {
            "type": "string"
            },
            "content_modified_at": {
            "type": "string"
            },
            "created_by": {
            "type": "object",
            "properties": {
                "type": {
                "type": "string"
                },
                "id": {
                "type": "string"
                },
                "name": {
                "type": "string"
                },
                "login": {
                "type": "string"
                }
            },
            "required": ["type", "id", "name", "login"]
            },
            "modified_by": {
            "type": "object",
            "properties": {
                "type": {
                "type": "string"
                },
                "id": {
                "type": "string"
                },
                "name": {
                "type": "string"
                },
                "login": {
                "type": "string"
                }
            },
            "required": ["type", "id", "name", "login"]
            },
            "owned_by": {
            "type": "object",
            "properties": {
                "type": {
                "type": "string"
                },
                "id": {
                "type": "string"
                },
                "name": {
                "type": "string"
                },
                "login": {
                "type": "string"
                }
            },
            "required": ["type", "id", "name", "login"]
            },
            "shared_link": {
            "type": "null"
            },
            "parent": {
            "type": "object",
            "properties": {
                "type": {
                "type": "string"
                },
                "id": {
                "type": "string"
                },
                "sequence_id": {
                "type": "string"
                },
                "etag": {
                "type": "string"
                },
                "name": {
                "type": "string"
                }
            },
            "required": ["type", "id", "sequence_id", "etag", "name"]
            },
            "item_status": {
            "type": "string"
            },
            "text_representation": {
            "type": "string"
            }
        }
        }

        """
    return json.loads(generic_schema)
