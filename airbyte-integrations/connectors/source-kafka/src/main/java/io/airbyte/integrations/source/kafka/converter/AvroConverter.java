package io.airbyte.integrations.source.kafka.converter;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.time.Instant;
import org.apache.avro.generic.GenericRecord;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AvroConverter implements Converter<GenericRecord> {

  private static final Logger LOGGER = LoggerFactory.getLogger(AvroConverter.class);

  @Override
  public AirbyteMessage convertToAirbyteRecord(String topic, GenericRecord value) {
    ObjectMapper mapper = new ObjectMapper();
    String namespace = value.getSchema().getNamespace();
    String name = value.getSchema().getName();
    JsonNode output;
    try {
      // Todo dynamic namespace is not supported now hence, adding avro schema name in the message
      if (StringUtils.isNoneEmpty(namespace) && StringUtils.isNoneEmpty(name)) {
        String newString = String.format("{\"avro_schema\": \"%s\",\"name\":\"%s\"}", namespace, name);
        JsonNode newNode = mapper.readTree(newString);
        output = mapper.readTree(value.toString());
        ((ObjectNode) output).set("_namespace_", newNode);
      } else {
        output = mapper.readTree(value.toString());
      }
    } catch (JsonProcessingException e) {
      LOGGER.error("Exception whilst reading avro data from stream", e);
      throw new RuntimeException(e);
    }
    return new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withStream(topic)
            .withEmittedAt(Instant.now().toEpochMilli())
            .withData(output));

  }
}
