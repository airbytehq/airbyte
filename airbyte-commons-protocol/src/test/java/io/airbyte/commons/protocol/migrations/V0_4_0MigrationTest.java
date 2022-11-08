package io.airbyte.commons.protocol.migrations;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStream;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class V0_4_0MigrationTest {

  private static final ObjectMapper MAPPER = new ObjectMapper();
  private static final String STREAM_NAME = "TEST_STREAM";

  private AirbyteMessageMigrationV0_4_0 migration;

  @BeforeEach
  public void setup() {
    migration = new AirbyteMessageMigrationV0_4_0();
  }

  @Test
  public void testVersionMetadata() {
    assertEquals("0.3.2", migration.getPreviousVersion().getMajorVersion());
    assertEquals("0.4.0", migration.getCurrentVersion().getMajorVersion());
  }

  @Test
  public void testBasicUpgrade() throws JsonProcessingException {
    JsonNode oldSchema = MAPPER.readTree("""
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

  private AirbyteMessage createCatalogMessage(JsonNode schema) {
    return new AirbyteMessage()
        .withType(Type.CATALOG)
        .withCatalog(new AirbyteCatalog()
            .withStreams(List.of(new AirbyteStream().withJsonSchema(schema))));
  }
}
