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
