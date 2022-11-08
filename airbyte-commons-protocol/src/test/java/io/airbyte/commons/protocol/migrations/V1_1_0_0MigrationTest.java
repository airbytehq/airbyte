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
import org.junit.jupiter.api.Test;

public class V1_1_0_0MigrationTest {

  private static final String STREAM_NAME = "TEST_STREAM";

  private AirbyteMessageMigrationV1_1_0 migration;

  @BeforeEach
  public void setup() {
    migration = new AirbyteMessageMigrationV1_1_0();
  }

  @Test
  public void testVersionMetadata() {
    assertEquals("1.0.0", migration.getPreviousVersion().serialize());
    assertEquals("1.1.0", migration.getCurrentVersion().serialize());
  }

  @Test
  public void testBasicUpgrade() {
    // This isn't actually a valid stream schema (since it's not an object)
    // but
    JsonNode oldSchema = Jsons.deserialize("""
        {
          "type": "string"
        }
        """);

    io.airbyte.protocol.models.v0.AirbyteMessage upgradedMessage = migration.upgrade(createCatalogMessage(oldSchema));

    io.airbyte.protocol.models.v0.AirbyteMessage expectedMessage = Jsons.deserialize(
        """
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
            """,
        io.airbyte.protocol.models.v0.AirbyteMessage.class
    );
    assertEquals(
        expectedMessage,
        upgradedMessage
    );
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

    JsonNode expectedSchema = Jsons.deserialize(
        """
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
                "example_timestamp_without_tz": {
                  "$ref": "WellKnownTypes.json#definitions/TimestampWithoutTimezone"
                },
                "example_timez": {
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
            """
    );
    assertEquals(
        expectedSchema,
        upgradedMessage.getCatalog().getStreams().get(0).getJsonSchema()
    );
  }

  private AirbyteMessage createCatalogMessage(JsonNode schema) {
    return new AirbyteMessage()
        .withType(Type.CATALOG)
        .withCatalog(new AirbyteCatalog()
            .withStreams(List.of(new AirbyteStream().withJsonSchema(schema))));
  }
}
