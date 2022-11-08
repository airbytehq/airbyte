package io.airbyte.commons.protocol.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableSet;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStream;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;
import java.util.Set;
import java.util.function.Consumer;
import java.util.function.Function;

public class AirbyteMessageMigrationV0_4_0 implements AirbyteMessageMigration<AirbyteMessage, io.airbyte.protocol.models.v0.AirbyteMessage> {

  private static final Set<String> PRIMITIVE_TYPES = ImmutableSet.of(
    "string",
    "number",
    "integer",
    "boolean"
  );

  @Override
  public AirbyteMessage downgrade(io.airbyte.protocol.models.v0.AirbyteMessage oldMessage) {
    return null;
  }

  @Override
  public io.airbyte.protocol.models.v0.AirbyteMessage upgrade(AirbyteMessage oldMessage) {
    // We're not introducing any changes to the structure of the record/catalog
    // so just clone a new message object, which we can edit in-place
    io.airbyte.protocol.models.v0.AirbyteMessage newMessage = Jsons.object(
        Jsons.jsonNode(oldMessage),
        io.airbyte.protocol.models.v0.AirbyteMessage.class);
    if (oldMessage.getType() == Type.CATALOG) {
      for (AirbyteStream stream : newMessage.getCatalog().getStreams()) {
        JsonNode schema = stream.getJsonSchema().deepCopy();
        mutate(
            s -> false,
            s -> {},
            schema);
      }
    } else if (oldMessage.getType() == Type.RECORD) {
      // TODO upgrade record
    }
    return newMessage;
  }

  /**
   * Recurses through all type declarations in the schema. For each type declaration that are accepted by matcher,
   * mutate them using transformer. For all other type declarations, recurse into them.
   *
   * @param schema The JsonSchema node to walk down
   * @param matcher A function which returns true on any schema node that needs to be transformed
   * @param transformer A function which mutates a schema node
   */
  private void mutate(Function<JsonNode, Boolean> matcher, Consumer<JsonNode> transformer, JsonNode schema) {
    if (matcher.apply(schema)) {
      transformer.accept(schema);
    } else {
      List<JsonNode> subschemas = new ArrayList<>();
      addAllSubschemas(subschemas, schema, "items");
      addAllSubschemas(subschemas, schema, "allOf");
      addAllSubschemas(subschemas, schema, "oneOf");
      addAllSubschemas(subschemas, schema, "anyOf");
      addAllSubschemas(subschemas, schema, "additionalProperties");

      addAllSubschemas(subschemas, schema, "properties");
      if (schema.hasNonNull("properties")) {
        ObjectNode propertiesNode = (ObjectNode)schema.get("properties");
        Iterator<Entry<String, JsonNode>> propertiesIterator = propertiesNode.fields();
        while (propertiesIterator.hasNext()) {
          Entry<String, JsonNode> property = propertiesIterator.next();
          subschemas.add(property.getValue());
        }
      }

      subschemas.forEach(subschema -> mutate(matcher, transformer, subschema));
    }
  }

  private static void addAllSubschemas(List<JsonNode> subschemas, JsonNode schema, String key) {
    if (schema.hasNonNull(key)) {
      JsonNode subschemaNode = schema.get(key);
      if (subschemaNode.isArray()) {
        for (JsonNode subschema : subschemaNode) {
          subschemas.add(subschema);
        }
      } else if (subschemaNode.isObject()) {
        subschemas.add(subschemaNode);
      } else {
        // TODO is this case possible?

        // additionalProperties: true/false
        // is it possible to have items: ["string"] ?
      }
    }
  }

  /**
   * Returns a copy of schema, with the primitive types replaced by the $ref types.
   */
  private static JsonNode upgradeSchema(JsonNode schema) {
    JsonNode typeNode = schema.get("type");
    if (typeNode == null || typeNode.isNull()) {
      // this shouldn't happen in a well-formed schema, but we should have handling for it just in case
      // just return the schema unmodified - this will probably blow up in the destination,
      // but we don't have any information about what it's _supposed_ to be, so we can't do anything here.
      return schema;
    }
    if (typeNode.isArray()) {
      ArrayNode typesArray = (ArrayNode) typeNode;
      List<String> types = new ArrayList<>();
      for (JsonNode typeElement : typesArray) {
        String type = typeElement.asText();
        if (!"null".equals(type)) {
          types.add(type);
        }
      }
      // TODO convert multi-type things into oneOf
    } else {
      String type = typeNode.asText();
      // TODO handle primitive vs non-primitive
      if (PRIMITIVE_TYPES.contains(type)) {
        return upgradePrimitiveSchema(schema);
      } else {

      }
    }
    return null;
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
