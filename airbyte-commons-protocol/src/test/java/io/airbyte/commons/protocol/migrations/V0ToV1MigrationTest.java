/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.Resources;

public class V0ToV1MigrationTest {


  JsonSchemaValidator validator;
  private AirbyteMessageMigrationV1 migration;

  @BeforeEach
  public void setup() throws URISyntaxException {
    URI parentUri = MoreResources.readResourceAsFile("WellKnownTypes.json").getAbsoluteFile().toURI();
    validator = new JsonSchemaValidator(parentUri);
    migration = new AirbyteMessageMigrationV1(null, validator);
  }

  @Test
  public void testVersionMetadata() {
    assertEquals("0.3.0", migration.getPreviousVersion().serialize());
    assertEquals("1.0.0", migration.getCurrentVersion().serialize());
  }

  @Nested
  public class CatalogUpgradeTest {

    @Test
    public void testBasicUpgrade() {
      // This isn't actually a valid stream schema (since it's not an object)
      // but this test case is mostly about preserving the message structure, so it's not super relevant
      JsonNode oldSchema = Jsons.deserialize(
          """
          {
            "type": "string"
          }
          """);

      AirbyteMessage upgradedMessage = migration.upgrade(createCatalogMessage(oldSchema));

      AirbyteMessage expectedMessage = Jsons.deserialize(
          """
          {
            "type": "CATALOG",
            "catalog": {
              "streams": [
                {
                  "json_schema": {
                    "$ref": "WellKnownTypes.json#/definitions/String"
                  }
                }
              ]
            }
          }
          """,
          AirbyteMessage.class);
      assertEquals(expectedMessage, upgradedMessage);
    }

    @Test
    public void testUpgradeAllPrimitives() {
      JsonNode oldSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "example_string": {
                "type": "string"
              },
              "example_number": {
                "type": "number"
              },
              "example_integer": {
                "type": "integer"
              },
              "example_airbyte_integer": {
                "type": "number",
                "airbyte_type": "integer"
              },
              "example_boolean": {
                "type": "boolean"
              },
              "example_timestamptz": {
                "type": "string",
                "format": "date-time",
                "airbyte_type": "timestamp_with_timezone"
              },
              "example_timestamptz_implicit": {
                "type": "string",
                "format": "date-time"
              },
              "example_timestamp_without_tz": {
                "type": "string",
                "format": "date-time",
                "airbyte_type": "timestamp_without_timezone"
              },
              "example_timez": {
                "type": "string",
                "format": "time",
                "airbyte_type": "time_with_timezone"
              },
              "example_timetz_implicit": {
                "type": "string",
                "format": "time"
              },
              "example_time_without_tz": {
                "type": "string",
                "format": "time",
                "airbyte_type": "time_without_timezone"
              },
              "example_date": {
                "type": "string",
                "format": "date"
              },
             "example_binary": {
               "type": "string",
               "contentEncoding": "base64"
             }
            }
          }
          """);

      AirbyteMessage upgradedMessage = migration.upgrade(createCatalogMessage(oldSchema));

      JsonNode expectedSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "example_string": {
                "$ref": "WellKnownTypes.json#/definitions/String"
              },
              "example_number": {
                "$ref": "WellKnownTypes.json#/definitions/Number"
              },
              "example_integer": {
                "$ref": "WellKnownTypes.json#/definitions/Integer"
              },
              "example_airbyte_integer": {
                "$ref": "WellKnownTypes.json#/definitions/Integer"
              },
              "example_boolean": {
                "$ref": "WellKnownTypes.json#/definitions/Boolean"
              },
              "example_timestamptz": {
                "$ref": "WellKnownTypes.json#/definitions/TimestampWithTimezone"
              },
              "example_timestamptz_implicit": {
                "$ref": "WellKnownTypes.json#/definitions/TimestampWithTimezone"
              },
              "example_timestamp_without_tz": {
                "$ref": "WellKnownTypes.json#/definitions/TimestampWithoutTimezone"
              },
              "example_timez": {
                "$ref": "WellKnownTypes.json#/definitions/TimeWithTimezone"
              },
              "example_timetz_implicit": {
                "$ref": "WellKnownTypes.json#/definitions/TimeWithTimezone"
              },
              "example_time_without_tz": {
                "$ref": "WellKnownTypes.json#/definitions/TimeWithoutTimezone"
              },
              "example_date": {
                "$ref": "WellKnownTypes.json#/definitions/Date"
              },
              "example_binary": {
                "$ref": "WellKnownTypes.json#/definitions/BinaryData"
              }
            }
          }
          """);
      assertEquals(expectedSchema, upgradedMessage.getCatalog().getStreams().get(0).getJsonSchema());
    }

    @Test
    public void testUpgradeNestedFields() {
      JsonNode oldSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "basic_array": {
                "items": {"type": "string"}
              },
              "tuple_array": {
                "items": [
                  {"type": "string"},
                  {"type": "integer"}
                ],
                "additionalItems": {"type": "string"},
                "contains": {"type": "integer"}
              },
              "nested_object": {
                "properties": {
                  "id": {"type": "integer"},
                  "nested_oneof": {
                    "oneOf": [
                      {"type": "string"},
                      {"type": "integer"}
                    ]
                  },
                  "nested_anyof": {
                    "anyOf": [
                      {"type": "string"},
                      {"type": "integer"}
                    ]
                  },
                  "nested_allof": {
                    "allOf": [
                      {"type": "string"},
                      {"type": "integer"}
                    ]
                  },
                  "nested_not": {
                    "not": [
                      {"type": "string"},
                      {"type": "integer"}
                    ]
                  }
                },
                "patternProperties": {
                  "integer_.*": {"type": "integer"}
                },
                "additionalProperties": {"type": "string"}
              }
            }
          }
          """);

      AirbyteMessage upgradedMessage = migration.upgrade(createCatalogMessage(oldSchema));

      JsonNode expectedSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "basic_array": {
                "items": {"$ref": "WellKnownTypes.json#/definitions/String"}
              },
              "tuple_array": {
                "items": [
                  {"$ref": "WellKnownTypes.json#/definitions/String"},
                  {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                ],
                "additionalItems": {"$ref": "WellKnownTypes.json#/definitions/String"},
                "contains": {"$ref": "WellKnownTypes.json#/definitions/Integer"}
              },
              "nested_object": {
                "properties": {
                  "id": {"$ref": "WellKnownTypes.json#/definitions/Integer"},
                  "nested_oneof": {
                    "oneOf": [
                      {"$ref": "WellKnownTypes.json#/definitions/String"},
                      {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                    ]
                  },
                  "nested_anyof": {
                    "anyOf": [
                      {"$ref": "WellKnownTypes.json#/definitions/String"},
                      {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                    ]
                  },
                  "nested_allof": {
                    "allOf": [
                      {"$ref": "WellKnownTypes.json#/definitions/String"},
                      {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                    ]
                  },
                  "nested_not": {
                    "not": [
                      {"$ref": "WellKnownTypes.json#/definitions/String"},
                      {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                    ]
                  }
                },
                "patternProperties": {
                  "integer_.*": {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                },
                "additionalProperties": {"$ref": "WellKnownTypes.json#/definitions/String"}
              }
            }
          }
          """);
      assertEquals(expectedSchema, upgradedMessage.getCatalog().getStreams().get(0).getJsonSchema());
    }

    @Test
    public void testUpgradeBooleanSchemas() {
      // Most of these should never happen in reality, but let's handle them just in case
      // The only ones that we're _really_ expecting are additionalItems and additionalProperties
      String schemaString = """
                            {
                              "type": "object",
                              "properties": {
                                "basic_array": {
                                  "items": true
                                },
                                "tuple_array": {
                                  "items": [true],
                                  "additionalItems": true,
                                  "contains": true
                                },
                                "nested_object": {
                                  "properties": {
                                    "id": true,
                                    "nested_oneof": {
                                      "oneOf": [true]
                                    },
                                    "nested_anyof": {
                                      "anyOf": [true]
                                    },
                                    "nested_allof": {
                                      "allOf": [true]
                                    },
                                    "nested_not": {
                                      "not": [true]
                                    }
                                  },
                                  "patternProperties": {
                                    "integer_.*": true
                                  },
                                  "additionalProperties": true
                                }
                              }
                            }
                            """;
      assertUpgradeIsNoop(schemaString);
    }

    @Test
    public void testUpgradeEmptySchema() {
      // Sources shouldn't do this, but we should have handling for it anyway, since it's not currently
      // enforced by SATs
      String schemaString = """
                            {
                              "type": "object",
                              "properties": {
                                "basic_array": {
                                  "items": {}
                                },
                                "tuple_array": {
                                  "items": [{}],
                                  "additionalItems": {},
                                  "contains": {}
                                },
                                "nested_object": {
                                  "properties": {
                                    "id": {},
                                    "nested_oneof": {
                                      "oneOf": [{}]
                                    },
                                    "nested_anyof": {
                                      "anyOf": [{}]
                                    },
                                    "nested_allof": {
                                      "allOf": [{}]
                                    },
                                    "nested_not": {
                                      "not": [{}]
                                    }
                                  },
                                  "patternProperties": {
                                    "integer_.*": {}
                                  },
                                  "additionalProperties": {}
                                }
                              }
                            }
                            """;
      assertUpgradeIsNoop(schemaString);
    }

    @Test
    public void testUpgradeLiteralSchema() {
      // Verify that we do _not_ recurse into places we shouldn't
      String schemaString = """
                            {
                              "type": "object",
                              "properties": {
                                "example_schema": {
                                  "type": "object",
                                  "default": {"type": "string"},
                                  "enum": [{"type": "string"}],
                                  "const": {"type": "string"}
                                }
                              }
                            }
                            """;
      assertUpgradeIsNoop(schemaString);
    }

    @Test
    public void testUpgradeMalformedSchemas() {
      // These schemas are "wrong" in some way. For example, normalization will currently treat
      // bad_timestamptz as a string timestamp_with_timezone,
      // i.e. it will disregard the option for a boolean.
      // Generating this sort of schema is just wrong; sources shouldn't do this to begin with. But let's
      // verify that we behave mostly correctly here.
      JsonNode oldSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "bad_timestamptz": {
                "type": ["boolean", "string"],
                "format": "date-time",
                "airbyte_type": "timestamp_with_timezone"
              },
              "bad_integer": {
                "type": "string",
                "format": "date-time",
                "airbyte_type": "integer"
              }
            }
          }
          """);

      AirbyteMessage upgradedMessage = migration.upgrade(createCatalogMessage(oldSchema));

      JsonNode expectedSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "bad_timestamptz": {"$ref": "WellKnownTypes.json#/definitions/TimestampWithTimezone"},
              "bad_integer": {"$ref": "WellKnownTypes.json#/definitions/Integer"}
            }
          }
          """);
      assertEquals(expectedSchema, upgradedMessage.getCatalog().getStreams().get(0).getJsonSchema());
    }

    @Test
    public void testUpgradeMultiTypeFields() {
      JsonNode oldSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "multityped_field": {
                "type": ["string", "object", "array"],
                "properties": {
                  "id": {"type": "string"}
                },
                "patternProperties": {
                  "integer_.*": {"type": "integer"}
                },
                "additionalProperties": {"type": "string"},
                "items": {"type": "string"},
                "additionalItems": {"type": "string"},
                "contains": {"type": "string"}
              },
              "nullable_multityped_field": {
                "type": ["null", "string", "array", "object"],
                "items": [{"type": "string"}, {"type": "integer"}],
                "properties": {
                  "id": {"type": "integer"}
                }
              },
              "multityped_date_field": {
                "type": ["string", "integer"],
                "format": "date"
              },
              "sneaky_singletype_field": {
                "type": ["string", "null"],
                "format": "date-time"
              }
            }
          }
          """);

      AirbyteMessage upgradedMessage = migration.upgrade(createCatalogMessage(oldSchema));

      JsonNode expectedSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "multityped_field": {
                "oneOf": [
                  {"$ref": "WellKnownTypes.json#/definitions/String"},
                  {
                    "type": "object",
                    "properties": {
                      "id": {"$ref": "WellKnownTypes.json#/definitions/String"}
                    },
                    "patternProperties": {
                      "integer_.*": {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                    },
                    "additionalProperties": {"$ref": "WellKnownTypes.json#/definitions/String"}
                  },
                  {
                    "type": "array",
                    "items": {"$ref": "WellKnownTypes.json#/definitions/String"},
                    "additionalItems": {"$ref": "WellKnownTypes.json#/definitions/String"},
                    "contains": {"$ref": "WellKnownTypes.json#/definitions/String"}
                  }
                ]
              },
              "nullable_multityped_field": {
                "oneOf": [
                  {"$ref": "WellKnownTypes.json#/definitions/String"},
                  {
                    "type": "array",
                    "items": [
                      {"$ref": "WellKnownTypes.json#/definitions/String"},
                      {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                    ]
                  },
                  {
                    "type": "object",
                    "properties": {
                      "id": {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                    }
                  }
                ]
              },
              "multityped_date_field": {
                "oneOf": [
                  {"$ref": "WellKnownTypes.json#/definitions/Date"},
                  {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                ]
              },
              "sneaky_singletype_field": {"$ref": "WellKnownTypes.json#/definitions/TimestampWithTimezone"}
            }
          }
          """);
      assertEquals(expectedSchema, upgradedMessage.getCatalog().getStreams().get(0).getJsonSchema());
    }

    private io.airbyte.protocol.models.v0.AirbyteMessage createCatalogMessage(JsonNode schema) {
      return new io.airbyte.protocol.models.v0.AirbyteMessage().withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.CATALOG)
          .withCatalog(
              new io.airbyte.protocol.models.v0.AirbyteCatalog().withStreams(List.of(new io.airbyte.protocol.models.v0.AirbyteStream().withJsonSchema(
                  schema))));
    }

    private void assertUpgradeIsNoop(String schemaString) {
      JsonNode oldSchema = Jsons.deserialize(schemaString);

      AirbyteMessage upgradedMessage = migration.upgrade(createCatalogMessage(oldSchema));

      JsonNode expectedSchema = Jsons.deserialize(schemaString);
      assertEquals(expectedSchema, upgradedMessage.getCatalog().getStreams().get(0).getJsonSchema());
    }

  }

  @Nested
  public class RecordUpgradeTest {

    @Test
    public void testBasicUpgrade() {
      JsonNode oldData = Jsons.deserialize(
          """
          {
            "id": 42
          }
          """);

      AirbyteMessage upgradedMessage = migration.upgrade(createRecordMessage(oldData));

      AirbyteMessage expectedMessage = Jsons.deserialize(
          """
          {
            "type": "RECORD",
            "record": {
              "data": {
                "id": "42"
              }
            }
          }
          """,
          AirbyteMessage.class);
      assertEquals(expectedMessage, upgradedMessage);
    }

    @Test
    public void testNestedUpgrade() {
      JsonNode oldData = Jsons.deserialize(
          """
          {
            "int": 42,
            "float": 42.0,
            "float2": 42.2,
            "sub_object": {
              "sub_int": 42,
              "sub_float": 42.0,
              "sub_float2": 42.2
            },
            "sub_array": [42, 42.0, 42.2]
          }
          """);

      AirbyteMessage upgradedMessage = migration.upgrade(createRecordMessage(oldData));

      JsonNode expectedData = Jsons.deserialize(
          """
          {
            "int": "42",
            "float": "42.0",
            "float2": "42.2",
            "sub_object": {
              "sub_int": "42",
              "sub_float": "42.0",
              "sub_float2": "42.2"
            },
            "sub_array": ["42", "42.0", "42.2"]
          }
          """);
      assertEquals(expectedData, upgradedMessage.getRecord().getData());
    }

    @Test
    public void testNonUpgradableValues() {
      JsonNode oldData = Jsons.deserialize(
          """
          {
            "boolean": true,
            "string": "arst",
            "sub_object": {
              "boolean": true,
              "string": "arst"
            },
            "sub_array": [true, "arst"]
          }
          """);

      AirbyteMessage upgradedMessage = migration.upgrade(createRecordMessage(oldData));

      JsonNode expectedData = Jsons.deserialize(
          """
          {
            "boolean": true,
            "string": "arst",
            "sub_object": {
              "boolean": true,
              "string": "arst"
            },
            "sub_array": [true, "arst"]
          }
          """);
      assertEquals(expectedData, upgradedMessage.getRecord().getData());
    }

    private io.airbyte.protocol.models.v0.AirbyteMessage createRecordMessage(JsonNode data) {
      return new io.airbyte.protocol.models.v0.AirbyteMessage().withType(io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD)
          .withRecord(new io.airbyte.protocol.models.v0.AirbyteRecordMessage().withData(data));
    }

  }

  @Nested
  public class CatalogDowngradeTest {

    @Test
    public void testBasicDowngrade() {
      // This isn't actually a valid stream schema (since it's not an object)
      // but this test case is mostly about preserving the message structure, so it's not super relevant
      JsonNode newSchema = Jsons.deserialize(
          """
          {
            "$ref": "WellKnownTypes.json#/definitions/String"
          }
          """);

      io.airbyte.protocol.models.v0.AirbyteMessage downgradedMessage = migration.downgrade(createCatalogMessage(newSchema));

      io.airbyte.protocol.models.v0.AirbyteMessage expectedMessage = Jsons.deserialize(
          """
          {
            "type": "CATALOG",
            "catalog": {
              "streams": [
                {
                  "json_schema": {
                    "type": "string"
                  }
                }
              ]
            }
          }
          """,
          io.airbyte.protocol.models.v0.AirbyteMessage.class);
      assertEquals(expectedMessage, downgradedMessage);
    }

    @Test
    public void testUpgradeAllPrimitives() {
      JsonNode oldSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "example_string": {
                "$ref": "WellKnownTypes.json#/definitions/String"
              },
              "example_number": {
                "$ref": "WellKnownTypes.json#/definitions/Number"
              },
              "example_integer": {
                "$ref": "WellKnownTypes.json#/definitions/Integer"
              },
              "example_boolean": {
                "$ref": "WellKnownTypes.json#/definitions/Boolean"
              },
              "example_timestamptz": {
                "$ref": "WellKnownTypes.json#/definitions/TimestampWithTimezone"
              },
              "example_timestamp_without_tz": {
                "$ref": "WellKnownTypes.json#/definitions/TimestampWithoutTimezone"
              },
              "example_timez": {
                "$ref": "WellKnownTypes.json#/definitions/TimeWithTimezone"
              },
              "example_time_without_tz": {
                "$ref": "WellKnownTypes.json#/definitions/TimeWithoutTimezone"
              },
              "example_date": {
                "$ref": "WellKnownTypes.json#/definitions/Date"
              }
            }
          }
          """);

      io.airbyte.protocol.models.v0.AirbyteMessage downgradedMessage = migration.downgrade(createCatalogMessage(oldSchema));

      JsonNode expectedSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "example_string": {
                "type": "string"
              },
              "example_number": {
                "type": "number"
              },
              "example_integer": {
                "type": "integer"
              },
              "example_boolean": {
                "type": "boolean"
              },
              "example_timestamptz": {
                "type": "string",
                "airbyte_type": "timestamp_with_timezone",
                "format": "date-time"
              },
              "example_timestamp_without_tz": {
                "type": "string",
                "airbyte_type": "timestamp_without_timezone",
                "format": "date-time"
              },
              "example_timez": {
                "type": "string",
                "airbyte_type": "time_with_timezone",
                "format": "time"
              },
              "example_time_without_tz": {
                "type": "string",
                "airbyte_type": "time_without_timezone",
                "format": "time"
              },
              "example_date": {
                "type": "string",
                "format": "date"
              }
            }
          }
          """);
      assertEquals(expectedSchema, downgradedMessage.getCatalog().getStreams().get(0).getJsonSchema());
    }

    @Test
    public void testDowngradeNestedFields() {
      JsonNode oldSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "basic_array": {
                "items": {"$ref": "WellKnownTypes.json#/definitions/String"}
              },
              "tuple_array": {
                "items": [
                  {"$ref": "WellKnownTypes.json#/definitions/String"},
                  {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                ],
                "additionalItems": {"$ref": "WellKnownTypes.json#/definitions/String"},
                "contains": {"$ref": "WellKnownTypes.json#/definitions/Integer"}
              },
              "nested_object": {
                "properties": {
                  "id": {"$ref": "WellKnownTypes.json#/definitions/Integer"},
                  "nested_oneof": {
                    "oneOf": [
                      {"$ref": "WellKnownTypes.json#/definitions/String"},
                      {"$ref": "WellKnownTypes.json#/definitions/TimestampWithTimezone"}
                    ]
                  },
                  "nested_anyof": {
                    "anyOf": [
                      {"$ref": "WellKnownTypes.json#/definitions/String"},
                      {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                    ]
                  },
                  "nested_allof": {
                    "allOf": [
                      {"$ref": "WellKnownTypes.json#/definitions/String"},
                      {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                    ]
                  },
                  "nested_not": {
                    "not": [
                      {"$ref": "WellKnownTypes.json#/definitions/String"},
                      {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                    ]
                  }
                },
                "patternProperties": {
                  "integer_.*": {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                },
                "additionalProperties": {"$ref": "WellKnownTypes.json#/definitions/String"}
              }
            }
          }
          """);

      io.airbyte.protocol.models.v0.AirbyteMessage downgradedMessage = migration.downgrade(createCatalogMessage(oldSchema));

      JsonNode expectedSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "basic_array": {
                "items": {"type": "string"}
              },
              "tuple_array": {
                "items": [
                  {"type": "string"},
                  {"type": "integer"}
                ],
                "additionalItems": {"type": "string"},
                "contains": {"type": "integer"}
              },
              "nested_object": {
                "properties": {
                  "id": {"type": "integer"},
                  "nested_oneof": {
                    "oneOf": [
                      {"type": "string"},
                      {"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone"}
                    ]
                  },
                  "nested_anyof": {
                    "anyOf": [
                      {"type": "string"},
                      {"type": "integer"}
                    ]
                  },
                  "nested_allof": {
                    "allOf": [
                      {"type": "string"},
                      {"type": "integer"}
                    ]
                  },
                  "nested_not": {
                    "not": [
                      {"type": "string"},
                      {"type": "integer"}
                    ]
                  }
                },
                "patternProperties": {
                  "integer_.*": {"type": "integer"}
                },
                "additionalProperties": {"type": "string"}
              }
            }
          }
          """);
      assertEquals(expectedSchema, downgradedMessage.getCatalog().getStreams().get(0).getJsonSchema());
    }

    @Test
    public void testDowngradeBooleanSchemas() {
      // Most of these should never happen in reality, but let's handle them just in case
      // The only ones that we're _really_ expecting are additionalItems and additionalProperties
      String schemaString = """
                            {
                              "type": "object",
                              "properties": {
                                "basic_array": {
                                  "items": true
                                },
                                "tuple_array": {
                                  "items": [true],
                                  "additionalItems": true,
                                  "contains": true
                                },
                                "nested_object": {
                                  "properties": {
                                    "id": true,
                                    "nested_oneof": {
                                      "oneOf": [true]
                                    },
                                    "nested_anyof": {
                                      "anyOf": [true]
                                    },
                                    "nested_allof": {
                                      "allOf": [true]
                                    },
                                    "nested_not": {
                                      "not": [true]
                                    }
                                  },
                                  "patternProperties": {
                                    "integer_.*": true
                                  },
                                  "additionalProperties": true
                                }
                              }
                            }
                            """;
      assertDowngradeIsNoop(schemaString);
    }

    @Test
    public void testDowngradeEmptySchema() {
      // Sources shouldn't do this, but we should have handling for it anyway, since it's not currently
      // enforced by SATs
      String schemaString = """
                            {
                              "type": "object",
                              "properties": {
                                "basic_array": {
                                  "items": {}
                                },
                                "tuple_array": {
                                  "items": [{}],
                                  "additionalItems": {},
                                  "contains": {}
                                },
                                "nested_object": {
                                  "properties": {
                                    "id": {},
                                    "nested_oneof": {
                                      "oneOf": [{}]
                                    },
                                    "nested_anyof": {
                                      "anyOf": [{}]
                                    },
                                    "nested_allof": {
                                      "allOf": [{}]
                                    },
                                    "nested_not": {
                                      "not": [{}]
                                    }
                                  },
                                  "patternProperties": {
                                    "integer_.*": {}
                                  },
                                  "additionalProperties": {}
                                }
                              }
                            }
                            """;
      assertDowngradeIsNoop(schemaString);
    }

    @Test
    public void testDowngradeLiteralSchema() {
      // Verify that we do _not_ recurse into places we shouldn't
      String schemaString = """
                            {
                              "type": "object",
                              "properties": {
                                "example_schema": {
                                  "type": "object",
                                  "default": {"$ref": "WellKnownTypes.json#/definitions/String"},
                                  "enum": [{"$ref": "WellKnownTypes.json#/definitions/String"}],
                                  "const": {"$ref": "WellKnownTypes.json#/definitions/String"}
                                }
                              }
                            }
                            """;
      assertDowngradeIsNoop(schemaString);
    }

    @Test
    public void testDowngradeMultiTypeFields() {
      JsonNode oldSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "multityped_field": {
                "oneOf": [
                  {"$ref": "WellKnownTypes.json#/definitions/String"},
                  {
                    "type": "object",
                    "properties": {
                      "id": {"$ref": "WellKnownTypes.json#/definitions/String"}
                    },
                    "patternProperties": {
                      "integer_.*": {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                    },
                    "additionalProperties": {"$ref": "WellKnownTypes.json#/definitions/String"}
                  },
                  {
                    "type": "array",
                    "items": {"$ref": "WellKnownTypes.json#/definitions/String"},
                    "additionalItems": {"$ref": "WellKnownTypes.json#/definitions/String"},
                    "contains": {"$ref": "WellKnownTypes.json#/definitions/String"}
                  }
                ]
              },
              "multityped_date_field": {
                "oneOf": [
                  {"$ref": "WellKnownTypes.json#/definitions/Date"},
                  {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                ]
              },
              "boolean_field": {
                "oneOf": [
                  true,
                  {"$ref": "WellKnownTypes.json#/definitions/String"},
                  false
                ]
              },
              "conflicting_field": {
                "oneOf": [
                  {"type": "object", "properties": {"id": {"$ref": "WellKnownTypes.json#/definitions/String"}}},
                  {"type": "object", "properties": {"name": {"$ref": "WellKnownTypes.json#/definitions/String"}}},
                  {"$ref": "WellKnownTypes.json#/definitions/String"}
                ]
              },
              "conflicting_primitives": {
                "oneOf": [
                  {"$ref": "WellKnownTypes.json#/definitions/TimestampWithoutTimezone"},
                  {"$ref": "WellKnownTypes.json#/definitions/TimestampWithTimezone"}
                ]
              }
            }
          }
          """);

      io.airbyte.protocol.models.v0.AirbyteMessage downgradedMessage = migration.downgrade(createCatalogMessage(oldSchema));

      JsonNode expectedSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "multityped_field": {
                "type": ["string", "object", "array"],
                "properties": {
                  "id": {"type": "string"}
                },
                "patternProperties": {
                  "integer_.*": {"type": "integer"}
                },
                "additionalProperties": {"type": "string"},
                "items": {"type": "string"},
                "additionalItems": {"type": "string"},
                "contains": {"type": "string"}
              },
              "multityped_date_field": {
                "type": ["string", "integer"],
                "format": "date"
              },
              "boolean_field": {
                "oneOf": [
                  true,
                  {"type": "string"},
                  false
                ]
              },
              "conflicting_field": {
                "oneOf": [
                  {"type": "object", "properties": {"id": {"type": "string"}}},
                  {"type": "object", "properties": {"name": {"type": "string"}}},
                  {"type": "string"}
                ]
              },
              "conflicting_primitives": {
                "oneOf": [
                  {"type": "string", "format": "date-time", "airbyte_type": "timestamp_without_timezone"},
                  {"type": "string", "format": "date-time", "airbyte_type": "timestamp_with_timezone"}
                ]
              }
            }
          }
          """);
      assertEquals(expectedSchema, downgradedMessage.getCatalog().getStreams().get(0).getJsonSchema());
    }

    @Test
    public void testDowngradeWeirdSchemas() {
      // old_style_schema isn't actually valid (i.e. v1 schemas should always be using $ref)
      // but we should check that it behaves well anyway
      JsonNode oldSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "old_style_schema": {"type": "string"}
            }
          }
          """);

      io.airbyte.protocol.models.v0.AirbyteMessage downgradedMessage = migration.downgrade(createCatalogMessage(oldSchema));

      JsonNode expectedSchema = Jsons.deserialize(
          """
          {
            "type": "object",
            "properties": {
              "old_style_schema": {"type": "string"}
            }
          }
          """);
      assertEquals(expectedSchema, downgradedMessage.getCatalog().getStreams().get(0).getJsonSchema());
    }

    private AirbyteMessage createCatalogMessage(JsonNode schema) {
      return new AirbyteMessage().withType(AirbyteMessage.Type.CATALOG)
          .withCatalog(
              new AirbyteCatalog().withStreams(List.of(new AirbyteStream().withJsonSchema(
                  schema))));
    }

    private void assertDowngradeIsNoop(String schemaString) {
      JsonNode oldSchema = Jsons.deserialize(schemaString);

      io.airbyte.protocol.models.v0.AirbyteMessage downgradedMessage = migration.downgrade(createCatalogMessage(oldSchema));

      JsonNode expectedSchema = Jsons.deserialize(schemaString);
      assertEquals(expectedSchema, downgradedMessage.getCatalog().getStreams().get(0).getJsonSchema());
    }

  }

  @Nested
  public class RecordDowngradeTest {

    private static final String STREAM_NAME = "foo_stream";
    private static final String NAMESPACE_NAME = "foo_namespace";

    @Test
    public void testBasicDowngrade() {
      ConfiguredAirbyteCatalog catalog = createConfiguredAirbyteCatalog(
          """
              {"$ref": "WellKnownTypes.json#/definitions/Integer"}
              """);
      JsonNode oldData = Jsons.deserialize(
          """
          "42"
          """);

      io.airbyte.protocol.models.v0.AirbyteMessage downgradedMessage = new AirbyteMessageMigrationV1(catalog, validator)
          .downgrade(createRecordMessage(oldData));

      io.airbyte.protocol.models.v0.AirbyteMessage expectedMessage = Jsons.deserialize(
          """
          {
            "type": "RECORD",
            "record": {
              "stream": "foo_stream",
              "namespace": "foo_namespace",
              "data": 42
            }
          }
          """,
          io.airbyte.protocol.models.v0.AirbyteMessage.class);
      assertEquals(expectedMessage, downgradedMessage);
    }

    @Test
    public void testNestedDowngrade() {
      ConfiguredAirbyteCatalog catalog = createConfiguredAirbyteCatalog(
          """
              {
                 "type": "object",
                 "properties": {
                  "int": {"$ref": "WellKnownTypes.json#/definitions/Integer"},
                  "num": {"$ref": "WellKnownTypes.json#/definitions/Number"},
                  "binary": {"$ref": "WellKnownTypes.json#/definitions/BinaryData"},
                  "bool": {"$ref": "WellKnownTypes.json#/definitions/Boolean"},
                  "object": {
                    "type": "object",
                    "properties": {
                      "int": {"$ref": "WellKnownTypes.json#/definitions/Integer"},
                      "arr": {
                        "type": "array",
                        "items": {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                      }
                    }
                  },
                  "array": {
                    "type": "array",
                    "items": {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                  },
                  "array_multitype": {
                    "type": "array",
                    "items": [{"$ref": "WellKnownTypes.json#/definitions/Integer"}, {"$ref": "WellKnownTypes.json#/definitions/String"}]
                  },
                  "oneof": {
                    "type": "array",
                    "items": {
                      "oneOf": [
                        {"$ref": "WellKnownTypes.json#/definitions/Integer"},
                        {"$ref": "WellKnownTypes.json#/definitions/Boolean"}
                      ]
                    }
                  }
                }
              }
              """
      );
      JsonNode oldData = Jsons.deserialize(
          """
          {
            "int": "42",
            "num": "43.2",
            "string": "42",
            "bool": true,
            "object": {
              "int": "42"
            },
            "array": ["42"],
            "array_multitype": ["42", "42"],
            "oneof": ["42", true],
            "additionalProperty": "42"
          }
          """);

      io.airbyte.protocol.models.v0.AirbyteMessage downgradedMessage = new AirbyteMessageMigrationV1(catalog, validator)
          .downgrade(createRecordMessage(oldData));

      io.airbyte.protocol.models.v0.AirbyteMessage expectedMessage = Jsons.deserialize(
          """
          {
            "type": "RECORD",
            "record": {
              "stream": "foo_stream",
              "namespace": "foo_namespace",
              "data": {
                "int": 42,
                "num": 43.2,
                "string": "42",
                "bool": true,
                "object": {
                  "int": 42
                },
                "array": [42],
                "array_multitype": [42, "42"],
                "oneof": [42, true],
                "additionalProperty": "42"
              }
            }
          }
          """,
          io.airbyte.protocol.models.v0.AirbyteMessage.class);
      assertEquals(expectedMessage, downgradedMessage);
    }

    @Test
    public void testWeirdDowngrade() {
      ConfiguredAirbyteCatalog catalog = createConfiguredAirbyteCatalog(
          """
              {
                 "type": "object",
                 "properties": {
                  "raw_int": {"$ref": "WellKnownTypes.json#/definitions/Integer"},
                  "raw_num": {"$ref": "WellKnownTypes.json#/definitions/Number"},
                  "bad_int": {"$ref": "WellKnownTypes.json#/definitions/Integer"},
                  "typeless_object": {
                    "properties": {
                      "foo": {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                    }
                  },
                  "typeless_array": {
                    "items": {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                  },
                  "arr_obj_union1": {
                    "type": ["array", "object"],
                    "items": {
                      "type": "object",
                      "properties": {
                        "id": {"$ref": "WellKnownTypes.json#/definitions/Integer"},
                        "name": {"$ref": "WellKnownTypes.json#/definitions/String"}
                      }
                    },
                    "properties": {
                      "id": {"$ref": "WellKnownTypes.json#/definitions/Integer"},
                      "name": {"$ref": "WellKnownTypes.json#/definitions/String"}
                    }
                  },
                  "arr_obj_union2": {
                    "type": ["array", "object"],
                    "items": {
                      "type": "object",
                      "properties": {
                        "id": {"$ref": "WellKnownTypes.json#/definitions/Integer"},
                        "name": {"$ref": "WellKnownTypes.json#/definitions/String"}
                      }
                    },
                    "properties": {
                      "id": {"$ref": "WellKnownTypes.json#/definitions/Integer"},
                      "name": {"$ref": "WellKnownTypes.json#/definitions/String"}
                    }
                  }
                }
              }
              """
      );
      JsonNode oldData = Jsons.deserialize(
          """
          {
            "raw_int": 42,
            "raw_num": 43.2,
            "bad_int": "foo",
            "typeless_object": {
              "foo": "42"
            },
            "typeless_array": ["42"],
            "arr_obj_union1": [{"id": "42", "name": "arst"}, {"id": "43", "name": "qwfp"}],
            "arr_obj_union2": {"id": "42", "name": "arst"}
          }
          """);

      io.airbyte.protocol.models.v0.AirbyteMessage downgradedMessage = new AirbyteMessageMigrationV1(catalog, validator)
          .downgrade(createRecordMessage(oldData));

      io.airbyte.protocol.models.v0.AirbyteMessage expectedMessage = Jsons.deserialize(
          """
          {
            "type": "RECORD",
            "record": {
              "stream": "foo_stream",
              "namespace": "foo_namespace",
              "data": {
                "raw_int": 42,
                "raw_num": 43.2,
                "bad_int": "foo",
                "typeless_object": {
                  "foo": 42
                },
                "typeless_array": [42],
                "arr_obj_union1": [{"id": 42, "name": "arst"}, {"id": 43, "name": "qwfp"}],
                "arr_obj_union2": {"id": 42, "name": "arst"}
              }
            }
          }
          """,
          io.airbyte.protocol.models.v0.AirbyteMessage.class);
      assertEquals(expectedMessage, downgradedMessage);
    }

    @Test
    public void testEmptySchema() {
      // TODO more complex stuff
      ConfiguredAirbyteCatalog catalog = createConfiguredAirbyteCatalog(
          """
              {
                 "type": "object",
                 "properties": {
                   "empty_schema_primitive": {},
                   "empty_schema_array": {},
                   "empty_schema_object": {}
                 }
                }
              }
              """
      );
      JsonNode oldData = Jsons.deserialize(
          """
          {
            "empty_schema_primitive": "42",
            "empty_schema_array": ["42", false],
            "empty_schema_object": {"foo": "42"}
          }
          """);

      io.airbyte.protocol.models.v0.AirbyteMessage downgradedMessage = new AirbyteMessageMigrationV1(catalog, validator)
          .downgrade(createRecordMessage(oldData));

      io.airbyte.protocol.models.v0.AirbyteMessage expectedMessage = Jsons.deserialize(
          """
          {
            "type": "RECORD",
            "record": {
              "stream": "foo_stream",
              "namespace": "foo_namespace",
              "data": {
                "empty_schema_primitive": "42",
                "empty_schema_array": ["42", false],
                "empty_schema_object": {"foo": "42"}
              }
            }
          }
          """,
          io.airbyte.protocol.models.v0.AirbyteMessage.class);
      assertEquals(expectedMessage, downgradedMessage);
    }

    @Test
    public void testBacktracking() {
      // These test cases verify that we correctly choose the most-correct oneOf option.
      ConfiguredAirbyteCatalog catalog = createConfiguredAirbyteCatalog(
          """
              {
                 "type": "object",
                 "properties": {
                   "valid_option": {
                     "oneOf": [
                       {"$ref": "WellKnownTypes.json#/definitions/Boolean"},
                       {"$ref": "WellKnownTypes.json#/definitions/Integer"},
                       {"$ref": "WellKnownTypes.json#/definitions/String"}
                     ]
                   },
                   "all_invalid": {
                     "oneOf": [
                       {
                         "type": "array",
                         "items": {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                       },
                       {
                         "type": "array",
                         "items": {"$ref": "WellKnownTypes.json#/definitions/Boolean"}
                       }
                     ]
                   },
                   "nested_oneof": {
                     "oneOf": [
                       {
                         "type": "array",
                         "items": {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                       },
                       {
                         "type": "array",
                         "items": {
                           "type": "object",
                           "properties": {
                             "foo": {
                               "oneOf": [
                                 {"$ref": "WellKnownTypes.json#/definitions/Boolean"},
                                 {"$ref": "WellKnownTypes.json#/definitions/Integer"}
                               ]
                             }
                           }
                         }
                       }
                     ]
                   }
                 }
                }
              }
              """
      );
      JsonNode oldData = Jsons.deserialize(
          """
          {
            "valid_option": "42",
            "all_invalid": ["42", "arst"],
            "nested_oneof": [{"foo": "42"}]
          }
          """);

      io.airbyte.protocol.models.v0.AirbyteMessage downgradedMessage = new AirbyteMessageMigrationV1(catalog, validator)
          .downgrade(createRecordMessage(oldData));

      io.airbyte.protocol.models.v0.AirbyteMessage expectedMessage = Jsons.deserialize(
          """
          {
            "type": "RECORD",
            "record": {
              "stream": "foo_stream",
              "namespace": "foo_namespace",
              "data": {
                "valid_option": 42,
                "all_invalid": [42, "arst"],
                "nested_oneof": [{"foo": 42}]
              }
            }
          }
          """,
          io.airbyte.protocol.models.v0.AirbyteMessage.class);
      assertEquals(expectedMessage, downgradedMessage);
    }

    private ConfiguredAirbyteCatalog createConfiguredAirbyteCatalog(String schema) {
      return new ConfiguredAirbyteCatalog()
          .withStreams(List.of(new ConfiguredAirbyteStream().withStream(new io.airbyte.protocol.models.AirbyteStream()
              .withName(STREAM_NAME)
              .withNamespace(NAMESPACE_NAME)
              .withJsonSchema(Jsons.deserialize(schema)))));
    }

    private AirbyteMessage createRecordMessage(JsonNode data) {
      return new AirbyteMessage().withType(AirbyteMessage.Type.RECORD)
          .withRecord(new AirbyteRecordMessage().withStream(STREAM_NAME).withNamespace(NAMESPACE_NAME).withData(data));
    }

  }

}
