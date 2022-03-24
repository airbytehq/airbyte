/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.util;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;

public class BigQueryDenormalizedTestDataUtils {

  public static JsonNode getSchema() {
    return Jsons.deserialize("""
                             {
                                 "type": [
                                     "object"
                                 ],
                                 "properties": {
                                     "accepts_marketing_updated_at": {
                                         "type": [
                                             "null",
                                             "string"
                                         ],
                                         "format": "date-time"
                                     },
                                     "name": {
                                         "type": [
                                             "string"
                                         ]
                                     },
                                     "permission-list": {
                                         "type": [
                                             "array"
                                         ],
                                         "items": {
                                             "type": [
                                                 "object"
                                             ],
                                             "properties": {
                                                 "domain": {
                                                     "type": [
                                                         "string"
                                                     ]
                                                 },
                                                 "grants": {
                                                     "type": [
                                                         "array"
                                                     ],
                                                     "items": {
                                                         "type": [
                                                             "string"
                                                         ]
                                                     }
                                                 }
                                             }
                                         }
                                     }
                                 }
                             }
                             """);
  }

  public static JsonNode getAnyOfSchema() {
    return Jsons.deserialize("""
                             {
                                "type":"object",
                                "properties":{
                                    "id":{
                                        "type":[
                                            "null",
                                            "string"
                                        ]
                                    },
                                    "name":{
                                        "type":[
                                            "null",
                                            "string"
                                        ]
                                    },
                                    "type":{
                                        "type":[
                                            "null",
                                            "string"
                                        ]
                                    },
                                    "email":{
                                        "type":[
                                            "null",
                                            "string"
                                        ]
                                    },
                                    "avatar":{
                                        "type":[
                                            "null",
                                            "object"
                                        ],
                                        "properties":{
                                            "image_url":{
                                                "type":[
                                                    "null",
                                                    "string"
                                                ]
                                            }
                                        },
                                        "additionalProperties":false
                                    },
                                    "team_ids":{
                                        "anyOf":[
                                            {
                                                "type":"array",
                                                "items":{
                                                    "type":"integer"
                                                }
                                            },
                                            {
                                                "type":"null"
                                            }
                                        ]
                                    },
                                    "admin_ids":{
                                        "anyOf":[
                                            {
                                                "type":"array",
                                                "items":{
                                                    "type":"integer"
                                                }
                                            },
                                            {
                                                "type":"null"
                                            }
                                        ]
                                    },
                                    "all_of_field":{
                                        "allOf":[
                                            {
                                                "type":"array",
                                                "items":{
                                                    "type":"integer"
                                                }
                                            },
                                            {
                                                "type":"string"
                                            },
                                            {
                                                "type":"integer"
                                            }
                                        ]
                                    },
                                    "job_title":{
                                        "type":[
                                            "null",
                                            "string"
                                        ]
                                    },
                                    "has_inbox_seat":{
                                        "type":[
                                            "null",
                                            "boolean"
                                        ]
                                    },
                                    "away_mode_enabled":{
                                        "type":[
                                            "null",
                                            "boolean"
                                        ]
                                    },
                                    "away_mode_reassign":{
                                        "type":[
                                            "null",
                                            "boolean"
                                        ]
                                    }

                                },
                                "additionalProperties":false
                             }
                             """);
  }

  public static JsonNode getSchemaWithFormats() {
    return Jsons.deserialize("""
                             {
                                 "type": [
                                     "object"
                                 ],
                                 "properties": {
                                     "name": {
                                         "type": [
                                             "string"
                                         ]
                                     },
                                     "date_of_birth": {
                                         "type": [
                                             "string"
                                         ],
                                         "format": "date"
                                     },
                                     "updated_at": {
                                         "type": [
                                             "string"
                                         ],
                                         "format": "date-time"
                                     }
                                 }
                             }
                             """);
  }

  public static JsonNode getSchemaWithDateTime() {
    return Jsons.deserialize("""
                             {
                                 "type": [
                                     "object"
                                 ],
                                 "properties": {
                                     "updated_at": {
                                         "type": [
                                             "string"
                                         ],
                                         "format": "date-time"
                                     },
                                     "items": {
                                         "type": [
                                             "object"
                                         ],
                                         "properties": {
                                             "nested_datetime": {
                                                 "type": [
                                                     "string"
                                                 ],
                                                 "format": "date-time"
                                             }
                                         }
                                     }
                                 }
                             }
                             """);
  }

  public static JsonNode getSchemaWithInvalidArrayType() {
    return Jsons.deserialize("""
                             {
                                 "type": [
                                     "object"
                                 ],
                                 "properties": {
                                     "name": {
                                         "type": [
                                             "string"
                                         ]
                                     },
                                     "permission-list": {
                                         "type": [
                                             "array"
                                         ],
                                         "items": {
                                             "type": [
                                                 "object"
                                             ],
                                             "properties": {
                                                 "domain": {
                                                     "type": [
                                                         "string"
                                                     ]
                                                 },
                                                 "grants": {
                                                     "type": [
                                                         "array"
                                                         """ + // missed "items" element
        """
                                ]
                            }
                        }
                    }
                }
            }
        }
        """);

  }

  public static JsonNode getData() {
    return Jsons.deserialize("""
                             {
                                 "name": "Andrii",
                                 "accepts_marketing_updated_at": "2021-10-11T06:36:53-07:00",
                                 "permission-list": [
                                     {
                                         "domain": "abs",
                                         "grants": [
                                             "admin"
                                         ]
                                     },
                                     {
                                         "domain": "tools",
                                         "grants": [
                                             "read",
                                             "write"
                                         ]
                                     }
                                 ]
                             }
                             """);
  }

  public static JsonNode getDataWithFormats() {
    return Jsons.deserialize("""
                             {
                                 "name": "Andrii",
                                 "date_of_birth": "1996-01-25",
                                 "updated_at": "2021-10-11T06:36:53"
                             }
                             """);
  }

  public static JsonNode getAnyOfFormats() {
    return Jsons.deserialize("""
                             {
                                 "id": "ID",
                                 "name": "Andrii",
                                 "type": "some_type",
                                 "email": "email@email.com",
                                 "avatar": {
                                    "image_url": "url_to_avatar.jpg"
                                 },
                                 "team_ids": {
                                     "big_query_array": [1, 2, 3],
                                     "big_query_null": null
                                 },
                                 "admin_ids": {
                                     "big_query_array": [],
                                     "big_query_null": null
                                 },
                                 "all_of_field": {
                                     "big_query_array": [4, 5, 6],
                                     "big_query_string": "Some text",
                                     "big_query_integer": 42
                                 },
                                 "job_title": "title",
                                 "has_inbox_seat": true,
                                 "away_mode_enabled": false,
                                 "away_mode_reassign": false
                             }
                             """);
  }

  public static JsonNode getAnyOfFormatsWithNull() {
    return Jsons.deserialize("""
                             {
                                 "name": "Mukola",
                                 "team_ids": null,
                                 "all_of_field": null,
                                 "avatar": null
                             }
                             """);
  }

  public static JsonNode getAnyOfFormatsWithEmptyList() {
    return Jsons.deserialize("""
                             {
                                 "name": "Sergii",
                                 "team_ids": [],
                                 "all_of_field": {
                                     "big_query_array": [4, 5, 6],
                                     "big_query_string": "Some text",
                                     "big_query_integer": 42
                                 }
                             }
                             """);
  }

  public static JsonNode getDataWithJSONDateTimeFormats() {
    return Jsons.deserialize("""
                             {
                               "updated_at": "2021-10-11T06:36:53+00:00",
                               "items": {
                                 "nested_datetime": "2021-11-11T06:36:53+00:00"
                               }
                             }
                             """);
  }

  public static JsonNode getDataWithJSONWithReference() {
    return Jsons.jsonNode(
        ImmutableMap.of("users", ImmutableMap.of(
            "name", "John",
            "surname", "Adams")));
  }

  public static JsonNode getSchemaWithReferenceDefinition() {
    return Jsons.deserialize("""
                             {
                                 "type": [
                                     "null",
                                     "object"
                                 ],
                                 "properties": {
                                     "users": {
                                         "$ref": "#/definitions/users_"
                                     }
                                 }
                             }
                             """);
  }

  public static JsonNode getSchemaWithNestedDatetimeInsideNullObject() {
    return Jsons.deserialize("""
                             {
                                 "type": [
                                     "object"
                                 ],
                                 "properties": {
                                     "name": {
                                         "type": [
                                             "null",
                                             "string"
                                         ]
                                     },
                                     "appointment": {
                                         "type": [
                                             "null",
                                             "object"
                                         ],
                                         "properties": {
                                             "street": {
                                                 "type": [
                                                     "null",
                                                     "string"
                                                 ]
                                             },
                                             "expTime": {
                                                 "type": [
                                                     "null",
                                                     "string"
                                                 ],
                                                 "format": "date-time"
                                             }
                                         }
                                     }
                                 }
                             }
                             """);
  }

  public static JsonNode getDataWithEmptyObjectAndArray() {
    return Jsons.deserialize("""
                             {
                                 "name": "Andrii",
                                 "permission-list": [
                                     {
                                         "domain": "abs",
                                         "items": {},
                                          """ + // empty object
        """
            "grants": [
                "admin"
            ]
        },
        {
            "domain": "tools",
            "grants": [],
            """ + // empty array
        """
        "items": {
        """ + // object with empty array and object
        """
                        "object": {},
                        "array": []
                    }
                }
            ]
        }
        """);
  }

  public static JsonNode getDataWithNestedDatetimeInsideNullObject() {
    return Jsons.deserialize("""
                             {
                                 "name": "Alice in Wonderland",
                                 "appointment": null
                             }
                                     """);

  }

}
