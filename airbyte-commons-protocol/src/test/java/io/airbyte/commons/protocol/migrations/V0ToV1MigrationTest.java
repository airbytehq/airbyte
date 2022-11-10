package io.airbyte.commons.protocol.migrations;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStream;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

public class V0ToV1MigrationTest {

  private AirbyteMessageMigrationV1 migration;

  @BeforeEach
  public void setup() {
    migration = new AirbyteMessageMigrationV1();
  }

  @Test
  public void testVersionMetadata() {
    assertEquals("0.0.0", migration.getPreviousVersion().serialize());
    assertEquals("1.0.0", migration.getCurrentVersion().serialize());
  }

  @Nested
  public class CatalogUpgradeTest {
    @Test
    public void testBasicUpgrade() {
      // This isn't actually a valid stream schema (since it's not an object)
      // but this test case is mostly about preserving the message structure, so it's not super relevant
      JsonNode oldSchema = Jsons.deserialize("""
        {
          "type": "string"
        }
        """);

      io.airbyte.protocol.models.v0.AirbyteMessage upgradedMessage = migration.upgrade(createCatalogMessage(oldSchema));

      io.airbyte.protocol.models.v0.AirbyteMessage expectedMessage = Jsons.deserialize("""
        {
          "type": "CATALOG",
          "catalog": {
            "streams": [
              {
                "json_schema": {
                  "$ref": "WellKnownTypes.json#definitions/String"
                }
              }
            ]
          }
        }
        """, io.airbyte.protocol.models.v0.AirbyteMessage.class);
      assertEquals(expectedMessage, upgradedMessage);
    }

    @Test
    public void testUpgradeAllPrimitives() {
      JsonNode oldSchema = Jsons.deserialize("""
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
            }
          }
        }
        """);

      io.airbyte.protocol.models.v0.AirbyteMessage upgradedMessage = migration.upgrade(createCatalogMessage(oldSchema));

      JsonNode expectedSchema = Jsons.deserialize("""
        {
          "type": "object",
          "properties": {
            "example_string": {
              "$ref": "WellKnownTypes.json#definitions/String"
            },
            "example_number": {
              "$ref": "WellKnownTypes.json#definitions/Number"
            },
            "example_integer": {
              "$ref": "WellKnownTypes.json#definitions/Integer"
            },
            "example_airbyte_integer": {
              "$ref": "WellKnownTypes.json#definitions/Integer"
            },
            "example_boolean": {
              "$ref": "WellKnownTypes.json#definitions/Boolean"
            },
            "example_timestamptz": {
              "$ref": "WellKnownTypes.json#definitions/TimestampWithTimezone"
            },
            "example_timestamptz_implicit": {
              "$ref": "WellKnownTypes.json#definitions/TimestampWithTimezone"
            },
            "example_timestamp_without_tz": {
              "$ref": "WellKnownTypes.json#definitions/TimestampWithoutTimezone"
            },
            "example_timez": {
              "$ref": "WellKnownTypes.json#definitions/TimeWithTimezone"
            },
            "example_timetz_implicit": {
              "$ref": "WellKnownTypes.json#definitions/TimeWithTimezone"
            },
            "example_time_without_tz": {
              "$ref": "WellKnownTypes.json#definitions/TimeWithoutTimezone"
            },
            "example_date": {
              "$ref": "WellKnownTypes.json#definitions/Date"
            }
          }
        }
        """);
      assertEquals(expectedSchema, upgradedMessage.getCatalog().getStreams().get(0).getJsonSchema());
    }

    @Test
    public void testUpgradeNestedFields() {
      JsonNode oldSchema = Jsons.deserialize("""
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

      io.airbyte.protocol.models.v0.AirbyteMessage upgradedMessage = migration.upgrade(createCatalogMessage(oldSchema));

      JsonNode expectedSchema = Jsons.deserialize("""
        {
          "type": "object",
          "properties": {
            "basic_array": {
              "items": {"$ref": "WellKnownTypes.json#definitions/String"}
            },
            "tuple_array": {
              "items": [
                {"$ref": "WellKnownTypes.json#definitions/String"},
                {"$ref": "WellKnownTypes.json#definitions/Integer"}
              ],
              "additionalItems": {"$ref": "WellKnownTypes.json#definitions/String"},
              "contains": {"$ref": "WellKnownTypes.json#definitions/Integer"}
            },
            "nested_object": {
              "properties": {
                "id": {"$ref": "WellKnownTypes.json#definitions/Integer"},
                "nested_oneof": {
                  "oneOf": [
                    {"$ref": "WellKnownTypes.json#definitions/String"},
                    {"$ref": "WellKnownTypes.json#definitions/Integer"}
                  ]
                },
                "nested_anyof": {
                  "anyOf": [
                    {"$ref": "WellKnownTypes.json#definitions/String"},
                    {"$ref": "WellKnownTypes.json#definitions/Integer"}
                  ]
                },
                "nested_allof": {
                  "allOf": [
                    {"$ref": "WellKnownTypes.json#definitions/String"},
                    {"$ref": "WellKnownTypes.json#definitions/Integer"}
                  ]
                },
                "nested_not": {
                  "not": [
                    {"$ref": "WellKnownTypes.json#definitions/String"},
                    {"$ref": "WellKnownTypes.json#definitions/Integer"}
                  ]
                }
              },
              "patternProperties": {
                "integer_.*": {"$ref": "WellKnownTypes.json#definitions/Integer"}
              },
              "additionalProperties": {"$ref": "WellKnownTypes.json#definitions/String"}
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
      // Sources shouldn't do this, but we should have handling for it anyway, since it's not currently enforced by SATs
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
      // These schemas are "wrong" in some way. For example, normalization will currently treat bad_timestamptz as a string timestamp_with_timezone,
      // i.e. it will disregard the option for a boolean.
      // Generating this sort of schema is just wrong; sources shouldn't do this to begin with. But let's verify that we behave mostly correctly here.
      JsonNode oldSchema = Jsons.deserialize("""
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

      io.airbyte.protocol.models.v0.AirbyteMessage upgradedMessage = migration.upgrade(createCatalogMessage(oldSchema));

      JsonNode expectedSchema = Jsons.deserialize("""
        {
          "type": "object",
          "properties": {
            "bad_timestamptz": {"$ref": "WellKnownTypes.json#definitions/TimestampWithTimezone"},
            "bad_integer": {"$ref": "WellKnownTypes.json#definitions/Integer"}
          }
        }
        """);
      assertEquals(expectedSchema, upgradedMessage.getCatalog().getStreams().get(0).getJsonSchema());
    }

    @Test
    public void testUpgradeMultiTypeFields() {
      JsonNode oldSchema = Jsons.deserialize("""
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

      io.airbyte.protocol.models.v0.AirbyteMessage upgradedMessage = migration.upgrade(createCatalogMessage(oldSchema));

      JsonNode expectedSchema = Jsons.deserialize("""
        {
          "type": "object",
          "properties": {
            "multityped_field": {
              "oneOf": [
                {"$ref": "WellKnownTypes.json#definitions/String"},
                {
                  "type": "object",
                  "properties": {
                    "id": {"$ref": "WellKnownTypes.json#definitions/String"}
                  },
                  "patternProperties": {
                    "integer_.*": {"$ref": "WellKnownTypes.json#definitions/Integer"}
                  },
                  "additionalProperties": {"$ref": "WellKnownTypes.json#definitions/String"}
                },
                {
                  "type": "array",
                  "items": {"$ref": "WellKnownTypes.json#definitions/String"},
                  "additionalItems": {"$ref": "WellKnownTypes.json#definitions/String"},
                  "contains": {"$ref": "WellKnownTypes.json#definitions/String"}
                }
              ]
            },
            "nullable_multityped_field": {
              "oneOf": [
                {"$ref": "WellKnownTypes.json#definitions/String"},
                {
                  "type": "array",
                  "items": [
                    {"$ref": "WellKnownTypes.json#definitions/String"},
                    {"$ref": "WellKnownTypes.json#definitions/Integer"}
                  ]
                },
                {
                  "type": "object",
                  "properties": {
                    "id": {"$ref": "WellKnownTypes.json#definitions/Integer"}
                  }
                }
              ]
            },
            "multityped_date_field": {
              "oneOf": [
                {"$ref": "WellKnownTypes.json#definitions/Date"},
                {"$ref": "WellKnownTypes.json#definitions/Integer"}
              ]
            },
            "sneaky_singletype_field": {"$ref": "WellKnownTypes.json#definitions/TimestampWithTimezone"}
          }
        }
        """);
      assertEquals(expectedSchema, upgradedMessage.getCatalog().getStreams().get(0).getJsonSchema());
    }
  }

  private AirbyteMessage createCatalogMessage(JsonNode schema) {
    return new AirbyteMessage().withType(Type.CATALOG)
        .withCatalog(new AirbyteCatalog().withStreams(List.of(new AirbyteStream().withJsonSchema(schema))));
  }

  private void assertUpgradeIsNoop(String schemaString) {
    JsonNode oldSchema = Jsons.deserialize(schemaString);

    io.airbyte.protocol.models.v0.AirbyteMessage upgradedMessage = migration.upgrade(createCatalogMessage(oldSchema));

    JsonNode expectedSchema = Jsons.deserialize(schemaString);
    assertEquals(expectedSchema, upgradedMessage.getCatalog().getStreams().get(0).getJsonSchema());
  }

}
