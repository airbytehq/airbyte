package io.airbyte.cdk.integrations.destination_async.dto;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonToken;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.deser.std.StdDeserializer;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMeta;
import java.io.IOException;
import java.util.Iterator;
import java.util.Map.Entry;

public class AirbyteRecordMessageDeserializer extends StdDeserializer<AirbyteRecordMessage> {

  public AirbyteRecordMessageDeserializer() {
    this(null);
  }

  public AirbyteRecordMessageDeserializer(Class<?> vc) {
    super(vc);
  }

  @Override
  public AirbyteRecordMessage deserialize(JsonParser jsonParser, DeserializationContext deserializationContext) throws IOException {
    final JsonNode node = jsonParser.getCodec().readTree(jsonParser);
    Iterator<Entry<String, JsonNode>> fields = node.fields();
    while (fields.hasNext()) {
      Entry<String, JsonNode> field = fields.next();
      System.out.println(field.getKey() + ":" + field.getValue() + "->" + field.getValue().isArray());
    }
    final JsonNode namespaceNode = node.get("namespace");
    final String namespace = namespaceNode != null && namespaceNode.isTextual() ? namespaceNode.asText() : null;
    final JsonNode streamNode = node.get("stream");
    final String stream = streamNode != null && streamNode.isTextual() ? streamNode.asText() : null;
    final JsonNode emittedAtNode = node.get("emitted_at");
    final long emittedAt = emittedAtNode != null && emittedAtNode.isNumber() ? emittedAtNode.asLong() : 0;
    final JsonNode dataNode = node.get("data");
    final JsonNode metaNode = node.get("meta");
    final String data = dataNode != null && dataNode.isObject() ? ((ObjectMapper)jsonParser.getCodec()).writeValueAsString(transformData(dataNode)) : null;
    final AirbyteRecordMessageMeta meta = metaNode != null && metaNode.isObject() ? ((ObjectMapper)jsonParser.getCodec()).convertValue(metaNode, AirbyteRecordMessageMeta.class) : null;
    return new AirbyteRecordMessage(namespace, stream, data, emittedAt, meta);
  }

  //  Using objectMapper interface is more readable than the below Streaming interface, with implicit dependency on a call to nextToken.
  private AirbyteRecordMessageMeta getMeta(JsonNode metaNode, JsonParser jsonParser, DeserializationContext deserializationContext) throws IOException {
    final AirbyteRecordMessageMeta meta;
    if (metaNode != null) {
      try (final JsonParser metaParser = metaNode.traverse(jsonParser.getCodec())) {
        // It is required to advance nextToken to initialize the subParser to correct location.
        if (metaParser.nextToken() == JsonToken.START_OBJECT) {
          meta = deserializationContext.readValue(metaParser, AirbyteRecordMessageMeta.class);
        } else {
          meta = null;
        }
      }
    } else {
      meta = null;
    }
    return meta;
  }

  private JsonNode transformData(JsonNode node) {
    Iterator<Entry<String, JsonNode>> fields = node.fields();
    while (fields.hasNext()) {
      Entry<String, JsonNode> field = fields.next();
      if (field.getKey().equals("integer")) {
        ((ObjectNode)node).put(field.getKey(), 1000);
      }
    }
    return node;
  }
}
