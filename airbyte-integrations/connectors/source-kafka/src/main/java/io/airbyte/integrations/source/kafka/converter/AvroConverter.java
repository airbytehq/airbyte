package io.airbyte.integrations.source.kafka.converter;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.time.Instant;
import org.apache.avro.generic.GenericRecord;
import org.apache.commons.lang3.StringUtils;

public class AvroConverter implements Converter<GenericRecord> {

  @Override
  public AirbyteMessage convertToAirbyteRecord(String topic, GenericRecord value) {
    String namespace = value.getSchema().getNamespace();
    String name = value.getSchema().getName();
    JsonNode output = Jsons.deserialize(value.toString());

    // Todo dynamic namespace is not supported now hence, adding avro schema name in the message
    if (StringUtils.isNoneEmpty(namespace) && StringUtils.isNoneEmpty(name)) {
      String newString = String.format("{ \"avro_schema\": \"%s\",\"name\": \"%s\" }", namespace, name);
      ((ObjectNode) output).set("_namespace_", Jsons.deserialize(newString));
    }

    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(topic)
            .withEmittedAt(Instant.now().toEpochMilli())
            .withData(output));

  }
}
