package io.airbyte.commons.protocol.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteRecordMessage;

public class AirbyteMessageMigrationV0_4_0 implements AirbyteMessageMigration<AirbyteMessage, io.airbyte.protocol.models.v0.AirbyteMessage> {

  @Override
  public AirbyteMessage downgrade(io.airbyte.protocol.models.v0.AirbyteMessage oldMessage) {
    return null;
  }

  @Override
  public io.airbyte.protocol.models.v0.AirbyteMessage upgrade(AirbyteMessage oldMessage) {
    io.airbyte.protocol.models.v0.AirbyteMessage newMessage = Jsons.object(
        Jsons.jsonNode(oldMessage),
        io.airbyte.protocol.models.v0.AirbyteMessage.class);
    if (oldMessage.getType() == Type.CATALOG) {
      io.airbyte.protocol.models.v0.AirbyteCatalog newCatalog = Jsons.object(
          Jsons.jsonNode(oldMessage.getCatalog()),
          io.airbyte.protocol.models.v0.AirbyteCatalog.class);
      // TODO upgrade catalog
      newMessage.setCatalog(newCatalog);
    } else if (oldMessage.getType() == Type.RECORD) {
      io.airbyte.protocol.models.v0.AirbyteRecordMessage newRecord = Jsons.object(
          Jsons.jsonNode(oldMessage.getRecord()),
          io.airbyte.protocol.models.v0.AirbyteRecordMessage.class);
      // TODO upgrade record
      newMessage.setRecord(newRecord);
    }
    return newMessage;
  }

  private static JsonNode upgradePrimitiveSchema(JsonNode primitiveSchema) {
    return null;
  }

  @Override
  public Version getPreviousVersion() {
    return new Version("0.3.2");
  }

  @Override
  public Version getCurrentVersion() {
    return new Version("0.4.0");
  }
}
