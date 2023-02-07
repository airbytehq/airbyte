/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations.v1;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

/**
 * These depend on the same {@link SchemaMigrationV1} class as
 * {@link io.airbyte.commons.protocol.migrations.v1.AirbyteMessageMigrationV1}. So, uh, I didn't
 * bother writing a ton of tests for it.
 *
 * Check out {@link AirbyteMessageMigrationV1} for more comprehensive tests. Theoretically
 * SchemaMigrationV1 should have its own set of tests, but for various (development history-related)
 * reasons, that would be a lot of work.
 */
class ConfiguredAirbyteCatalogMigrationV1Test {

  private ConfiguredAirbyteCatalogMigrationV1 migration;

  @BeforeEach
  void setup() {
    migration = new ConfiguredAirbyteCatalogMigrationV1();
  }

  @Test
  void testVersionMetadata() {
    assertEquals("0.3.0", migration.getPreviousVersion().serialize());
    assertEquals("1.0.0", migration.getCurrentVersion().serialize());
  }

  @Test
  void testBasicUpgrade() {
    // This isn't actually a valid stream schema (since it's not an object)
    // but this test case is mostly about preserving the message structure, so it's not super relevant
    final io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog downgradedCatalog = new io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog()
        .withStreams(List.of(
            new io.airbyte.protocol.models.v0.ConfiguredAirbyteStream().withStream(new io.airbyte.protocol.models.v0.AirbyteStream().withJsonSchema(
                Jsons.deserialize(
                    """
                    {
                      "type": "string"
                    }
                    """)))));

    final ConfiguredAirbyteCatalog upgradedMessage = migration.upgrade(downgradedCatalog);

    final ConfiguredAirbyteCatalog expectedMessage = Jsons.deserialize(
        """
        {
          "streams": [
            {
              "stream": {
                "json_schema": {
                  "$ref": "WellKnownTypes.json#/definitions/String"
                }
              }
            }
          ]
        }
        """,
        ConfiguredAirbyteCatalog.class);
    assertEquals(expectedMessage, upgradedMessage);
  }

  @Test
  void testBasicDowngrade() {
    // This isn't actually a valid stream schema (since it's not an object)
    // but this test case is mostly about preserving the message structure, so it's not super relevant
    final ConfiguredAirbyteCatalog upgradedCatalog = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(
            new ConfiguredAirbyteStream().withStream(new AirbyteStream().withJsonSchema(
                Jsons.deserialize("""
                                  {
                                    "$ref": "WellKnownTypes.json#/definitions/String"
                                  }
                                  """)))));

    final io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog downgradedMessage = migration.downgrade(upgradedCatalog);

    final io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog expectedMessage = Jsons.deserialize(
        """
        {
          "streams": [
            {
              "stream": {
                "json_schema": {
                  "type": "string"
                }
              }
            }
          ]
        }
        """,
        io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog.class);
    assertEquals(expectedMessage, downgradedMessage);
  }

}
