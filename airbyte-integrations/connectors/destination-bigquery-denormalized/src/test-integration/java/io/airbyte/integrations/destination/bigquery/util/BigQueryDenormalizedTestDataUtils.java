/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.util;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class BigQueryDenormalizedTestDataUtils {

  private static final String JSON_FILES_BASE_LOCATION = "testdata/";

  public static JsonNode getSchema() {
    return getTestDataFromResourceJson("schema.json");
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
    return getTestDataFromResourceJson("schemaWithFormats.json");
  }

  public static JsonNode getSchemaWithDateTime() {
    return getTestDataFromResourceJson("schemaWithDateTime.json");
  }

  public static JsonNode getSchemaWithInvalidArrayType() {
    return getTestDataFromResourceJson("schemaWithInvalidArrayType.json");
  }

  public static JsonNode getData() {
    return getTestDataFromResourceJson("data.json");
  }

  public static JsonNode getDataWithFormats() {
    return getTestDataFromResourceJson("dataWithFormats.json");
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
    return getTestDataFromResourceJson("dataWithJSONDateTimeFormats.json");
  }

  public static JsonNode getDataWithJSONWithReference() {
    return getTestDataFromResourceJson("dataWithJSONWithReference.json");
  }

  public static JsonNode getSchemaWithReferenceDefinition() {
    return getTestDataFromResourceJson("schemaWithReferenceDefinition.json");
  }

  public static JsonNode getSchemaWithNestedDatetimeInsideNullObject() {
    return getTestDataFromResourceJson("schemaWithNestedDatetimeInsideNullObject.json");
  }

  public static JsonNode getDataWithEmptyObjectAndArray() {
    return getTestDataFromResourceJson("dataWithEmptyObjectAndArray.json");
  }

  public static JsonNode getDataWithNestedDatetimeInsideNullObject() {
    return getTestDataFromResourceJson("dataWithNestedDatetimeInsideNullObject.json");

  }

  private static JsonNode getTestDataFromResourceJson(final String fileName) {
    final String fileContent;
    try {
      fileContent = Files.readString(Path.of(BigQueryDenormalizedTestDataUtils.class.getClassLoader()
          .getResource(JSON_FILES_BASE_LOCATION + fileName).getPath()));
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
    return Jsons.deserialize(fileContent);
  }

}
