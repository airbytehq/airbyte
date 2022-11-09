package io.airbyte.commons.protocol.migrations;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.ImmutableSet;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStream;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.StreamSupport;

public class AirbyteMessageMigrationV1_1_0 implements AirbyteMessageMigration<AirbyteMessage, io.airbyte.protocol.models.v0.AirbyteMessage> {

  private static final Set<String> PRIMITIVE_TYPES = ImmutableSet.of(
    "string",
    "number",
    "integer",
    "boolean"
  );
  private static final Map<String, String> AIRBYTE_TYPE_TO_REFERENCE_TYPE = ImmutableMap.of(
      "timestamp_with_timezone", "WellKnownTypes.json#definitions/TimestampWithTimezone",
      "timestamp_without_timezone", "WellKnownTypes.json#definitions/TimestampWithoutTimezone",
      "time_with_timezone", "WellKnownTypes.json#definitions/TimeWithTimezone",
      "time_without_timezone", "WellKnownTypes.json#definitions/TimeWithoutTimezone",
      "integer", "WellKnownTypes.json#definitions/Integer",
      // these types never actually use airbyte_type, but including them for consistency
      "string", "WellKnownTypes.json#definitions/String",
      "number", "WellKnownTypes.json#definitions/Number",
      "boolean", "WellKnownTypes.json#definitions/Boolean",
      "date", "WellKnownTypes.json#definitions/Date"
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
        JsonNode schema = stream.getJsonSchema();
        mutate(
            this::isPrimitiveTypeDeclaration,
            this::upgradeTypeDeclaration,
            schema);
      }
    } else if (oldMessage.getType() == Type.RECORD) {
      // TODO upgrade record
    }
    return newMessage;
  }

  /**
   * Detects any schema that looks like a primitive type declaration, e.g.:
   * { "type": "string" }
   * or
   * { "type": ["string", "object"] }
   */
  private boolean isPrimitiveTypeDeclaration(JsonNode schema) {
    if (!schema.isObject() || !schema.hasNonNull("type")) {
      return false;
    }
    JsonNode typeNode = schema.get("type");
    if (typeNode.isArray()) {
      return StreamSupport.stream(typeNode.iterator().next().spliterator(), false)
          .anyMatch(n -> PRIMITIVE_TYPES.contains(n.asText()));
    } else {
      return PRIMITIVE_TYPES.contains(typeNode.asText());
    }
  }

  /**
   * Modifies the schema in-place to upgrade from the old-style type declaration to the new-style $ref declaration.
   * @param schema An ObjectNode representing a primitive type declaration
   */
  private void upgradeTypeDeclaration(JsonNode schema) {
    ObjectNode schemaNode = (ObjectNode)schema;

    if (schemaNode.hasNonNull("airbyte_type")) {
      // airbyte_type always wins
      String referenceType = AIRBYTE_TYPE_TO_REFERENCE_TYPE.get(schemaNode.get("airbyte_type").asText());
      schemaNode.removeAll();
      schemaNode.put("$ref", referenceType);
    } else {
      // TODO handle when schema["type"] is a list
      String type = schemaNode.get("type").asText();
      switch (type) {
        case "string" -> {
          if (schemaNode.hasNonNull("format")) {
            switch (schemaNode.get("format").asText()) {
              case "date" -> {
                schemaNode.removeAll();
                schemaNode.put("$ref", "WellKnownTypes.json#definitions/Date");
              }
              // In these two cases, we default to the "with timezone" type, rather than "without timezone".
              case "date-time" -> {
                schemaNode.removeAll();
                schemaNode.put("$ref", "WellKnownTypes.json#definitions/TimestampWithTimezone");
              }
              case "time" -> {
                schemaNode.removeAll();
                schemaNode.put("$ref", "WellKnownTypes.json#definitions/TimeWithTimezone");
              }
            }
          } else {
            schemaNode.removeAll();
            schemaNode.put("$ref", "WellKnownTypes.json#definitions/String");
          }
        }
        case "integer" -> {
          schemaNode.removeAll();
          schemaNode.put("$ref", "WellKnownTypes.json#definitions/Integer");
        }
        case "number" -> {
          schemaNode.removeAll();
          schemaNode.put("$ref", "WellKnownTypes.json#definitions/Number");
        }
        case "boolean" -> {
          schemaNode.removeAll();
          schemaNode.put("$ref", "WellKnownTypes.json#definitions/Boolean");
        }
      }
    }
  }

  /**
   * Recurses through all type declarations in the schema. For each type declaration that are accepted by matcher,
   * mutate them using transformer. For all other type declarations, recurse into them.
   *
   * @param schema The JsonSchema node to walk down
   * @param matcher A function which returns true on any schema node that needs to be transformed
   * @param transformer A function which mutates a schema node
   */
  private static void mutate(Function<JsonNode, Boolean> matcher, Consumer<JsonNode> transformer, JsonNode schema) {
    if (schema.isBoolean()) {
      // We never want to modoify a schema of `true` or `false` (e.g. additionalProperties: true)
      // so just return immediately
      return;
    }
    if (matcher.apply(schema)) {
      // If this schema has a primitive type, then we need to mutate it
      transformer.accept(schema);
    } else {
      // Otherwise, we need to find all of the subschemas and mutate them.
      // technically, it might be more correct to do something like:
      //   if schema["type"] == "array": find subschemas for items, additionalItems, contains
      //   else if schema["type"] == "object": find subschemas for properties, additionalProperties
      //   else if oneof, allof, etc
      // but that sounds really verbose :shrug:
      List<JsonNode> subschemas = new ArrayList<>();

      findSubschemas(subschemas, schema, "items");
      findSubschemas(subschemas, schema, "additionalItems");
      findSubschemas(subschemas, schema, "contains");

      findSubschemas(subschemas, schema, "additionalProperties");

      // destinations have limited support for combining restrictions, but we should handle the schemas correctly anyway
      findSubschemas(subschemas, schema, "allOf");
      findSubschemas(subschemas, schema, "oneOf");
      findSubschemas(subschemas, schema, "anyOf");
      findSubschemas(subschemas, schema, "not");

      if (schema.hasNonNull("properties")) {
        ObjectNode propertiesNode = (ObjectNode)schema.get("properties");
        Iterator<Entry<String, JsonNode>> propertiesIterator = propertiesNode.fields();
        while (propertiesIterator.hasNext()) {
          Entry<String, JsonNode> property = propertiesIterator.next();
          subschemas.add(property.getValue());
        }
      }
      if (schema.hasNonNull("patternProperties")) {
        ObjectNode propertiesNode = (ObjectNode)schema.get("patternProperties");
        Iterator<Entry<String, JsonNode>> propertiesIterator = propertiesNode.fields();
        while (propertiesIterator.hasNext()) {
          Entry<String, JsonNode> property = propertiesIterator.next();
          subschemas.add(property.getValue());
        }
      }

      subschemas.forEach(subschema -> mutate(matcher, transformer, subschema));
    }
  }

  /**
   * If schema contains key, then grab the subschema(s) at schema[key] and add them to the subschemas list.
   */
  private static void findSubschemas(List<JsonNode> subschemas, JsonNode schema, String key) {
    if (schema.hasNonNull(key)) {
      JsonNode subschemaNode = schema.get(key);
      if (subschemaNode.isArray()) {
        for (JsonNode subschema : subschemaNode) {
          subschemas.add(subschema);
        }
      } else if (subschemaNode.isObject()) {
        subschemas.add(subschemaNode);
      }
    }
  }

  @Override
  public Version getPreviousVersion() {
    return new Version("1.0.0");
  }

  @Override
  public Version getCurrentVersion() {
    return new Version("1.1.0");
  }
}
