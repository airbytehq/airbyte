/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations.v1;

import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.REF_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.TextNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.protocol.migrations.AirbyteMessageMigration;
import io.airbyte.commons.protocol.migrations.util.SchemaMigrations;
import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import java.util.Optional;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.JsonSchemaReferenceTypes;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.validation.json.JsonSchemaValidator;
import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import java.util.Map.Entry;
import java.util.Objects;
import java.util.Optional;
import java.util.function.Consumer;
import java.util.function.Function;
import java.util.stream.StreamSupport;

public class AirbyteMessageMigrationV1 implements AirbyteMessageMigration<io.airbyte.protocol.models.v0.AirbyteMessage, AirbyteMessage> {

  private final ConfiguredAirbyteCatalog catalog;
  private final JsonSchemaValidator validator;

  public AirbyteMessageMigrationV1(ConfiguredAirbyteCatalog catalog, JsonSchemaValidator validator) {
    this.catalog = catalog;
    this.validator = validator;
  }

  @Override
<<<<<<< HEAD
  public AirbyteMessage downgrade(final io.airbyte.protocol.models.AirbyteMessage message,
                                  final Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog) {
    return Jsons.object(Jsons.jsonNode(message), AirbyteMessage.class);
=======
  public io.airbyte.protocol.models.v0.AirbyteMessage downgrade(AirbyteMessage oldMessage) {
    io.airbyte.protocol.models.v0.AirbyteMessage newMessage = Jsons.object(
        Jsons.jsonNode(oldMessage),
        io.airbyte.protocol.models.v0.AirbyteMessage.class);
    if (oldMessage.getType() == Type.CATALOG) {
      for (io.airbyte.protocol.models.v0.AirbyteStream stream : newMessage.getCatalog().getStreams()) {
        JsonNode schema = stream.getJsonSchema();
        SchemaMigrationV1.downgradeSchema(schema);
      }
    } else if (oldMessage.getType() == Type.RECORD) {
      io.airbyte.protocol.models.v0.AirbyteRecordMessage record = newMessage.getRecord();
      Optional<ConfiguredAirbyteStream> maybeStream = catalog.getStreams().stream()
          .filter(stream -> Objects.equals(stream.getStream().getName(), record.getStream())
              && Objects.equals(stream.getStream().getNamespace(), record.getNamespace()))
          .findFirst();
      // If this record doesn't belong to any configured stream, then there's no point downgrading it
      // So only do the downgrade if we can find its stream
      if (maybeStream.isPresent()) {
        JsonNode schema = maybeStream.get().getStream().getJsonSchema();
        JsonNode oldData = record.getData();
        DowngradedNode downgradedNode = downgradeNode(oldData, schema);
        record.setData(downgradedNode.node);
      }
    }
    return newMessage;
>>>>>>> 18c3e46222 (Data types update: Implement protocol message downgrade path (#19909))
  }

  @Override
  public AirbyteMessage upgrade(io.airbyte.protocol.models.v0.AirbyteMessage oldMessage) {
    // We're not introducing any changes to the structure of the record/catalog
    // so just clone a new message object, which we can edit in-place
    AirbyteMessage newMessage = Jsons.object(
        Jsons.jsonNode(oldMessage),
        AirbyteMessage.class);
    if (oldMessage.getType() == io.airbyte.protocol.models.v0.AirbyteMessage.Type.CATALOG) {
      for (AirbyteStream stream : newMessage.getCatalog().getStreams()) {
        JsonNode schema = stream.getJsonSchema();
        SchemaMigrationV1.upgradeSchema(schema);
      }
    } else if (oldMessage.getType() == io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD) {
      JsonNode oldData = newMessage.getRecord().getData();
      JsonNode newData = upgradeRecord(oldData);
      newMessage.getRecord().setData(newData);
    }
    return newMessage;
  }

  /**
   * Returns a copy of oldData, with numeric values converted to strings. String and boolean values
   * are returned as-is for convenience, i.e. this is not a true deep copy.
   */
  private static JsonNode upgradeRecord(JsonNode oldData) {
    if (oldData.isNumber()) {
      // Base case: convert numbers to strings
      return Jsons.convertValue(oldData.asText(), TextNode.class);
    } else if (oldData.isObject()) {
      // Recurse into each field of the object
      ObjectNode newData = (ObjectNode) Jsons.emptyObject();

      Iterator<Entry<String, JsonNode>> fieldsIterator = oldData.fields();
      while (fieldsIterator.hasNext()) {
        Entry<String, JsonNode> next = fieldsIterator.next();
        String key = next.getKey();
        JsonNode value = next.getValue();

        JsonNode newValue = upgradeRecord(value);
        newData.set(key, newValue);
      }

      return newData;
    } else if (oldData.isArray()) {
      // Recurse into each element of the array
      ArrayNode newData = Jsons.arrayNode();
      for (JsonNode element : oldData) {
        newData.add(upgradeRecord(element));
      }
      return newData;
    } else {
      // Base case: this is a string or boolean, so we don't need to modify it
      return oldData;
    }
  }

  /**
   * Quick and dirty tuple. Used internally by {@link #downgradeNode(JsonNode, JsonNode)}; callers
   * probably only actually need the node.
   *
   * matchedSchema is useful for downgrading using a oneOf schema, where we need to recognize the
   * correct subschema.
   *
   * @param node Our attempt at downgrading the node, under the given schema
   * @param matchedSchema Whether the original node actually matched the schema
   */
  private record DowngradedNode(JsonNode node, boolean matchedSchema) {}

  /**
   * We need the schema to recognize which fields are integers, since it would be wrong to just assume
   * any numerical string should be parsed out.
   *
   * Works on a best-effort basis. If the schema doesn't match the data, we'll do our best to
   * downgrade anything that we can definitively say is a number. Should _not_ throw an exception if
   * bad things happen (e.g. we try to parse a non-numerical string as a number).
   */
  private DowngradedNode downgradeNode(JsonNode data, JsonNode schema) {
    // If this is a oneOf node that looks like an upgraded v0 message, then we need to handle each oneOf
    // case.
    if (!schema.hasNonNull(REF_KEY) && !schema.hasNonNull("type") && schema.hasNonNull("oneOf")) {
      return downgradeOneofNode(data, schema);
    }
    // Otherwise, we need to do something specific to whatever the data is.
    if (data.isTextual()) {
      return downgradeTextualNode(data, schema);
    } else if (data.isObject()) {
      return downgradeObjectNode(data, schema);
    } else if (data.isArray()) {
      return downgradeArrayNode(data, schema);
    } else {
      // A primitive, non-text node never needs to be modified:
      // Protocol v1 didn't change how booleans work
      // And protocol v0 expects raw numbers anyway
      // So we just check whether the schema is correct and return the node as-is.
      return new DowngradedNode(data, validator.validate(schema, data).isEmpty());
    }
  }

  /**
   * Attempt to downgrade using each oneOf option in sequence. Returns the result from downgrading
   * using the first subschema that matches the data, or if none match, then the result of using the
   * first subschema.
   */
  private DowngradedNode downgradeOneofNode(JsonNode data, JsonNode schema) {
    JsonNode schemaOptions = schema.get("oneOf");
    if (schemaOptions.size() == 0) {
      // If the oneOf has no options, then don't do anything interesting.
      return new DowngradedNode(data, validator.validate(schema, data).isEmpty());
    }

    // Attempt to downgrade the node against each oneOf schema.
    // Return the first schema that matches the data, or the first schema if none matched successfully.
    DowngradedNode downgradedNode = null;
    for (JsonNode maybeSchema : schemaOptions) {
      DowngradedNode maybeDowngradedNode = downgradeNode(data, maybeSchema);
      if (downgradedNode == null) {
        // If this is the first subschema, then just take it
        downgradedNode = maybeDowngradedNode;
      } else if (!downgradedNode.matchedSchema() && maybeDowngradedNode.matchedSchema()) {
        // Otherwise - if we've found a matching schema, then return immediately
        downgradedNode = maybeDowngradedNode;
        break;
      }
    }
    // None of the schemas matched, so just return whatever we found first
    return downgradedNode;
  }

  /**
   * Downgrade a textual node. This could either be a string/date/timestamp/etc, in which case we need
   * to do nothing. Or it could be a number/integer, in which case we should convert it to a JSON
   * numerical node.
   *
   * If the data doesn't match the schema, then just return it without modification.
   */
  private DowngradedNode downgradeTextualNode(JsonNode data, JsonNode schema) {
    JsonNode refNode = schema.get(REF_KEY);
    if (refNode != null) {
      // If this is a valid v1 schema, then we _must_ have a $ref schema.
      String refType = refNode.asText();
      if (JsonSchemaReferenceTypes.NUMBER_REFERENCE.equals(refType)
          || JsonSchemaReferenceTypes.INTEGER_REFERENCE.equals(refType)) {
        // We could do this as a try-catch, but this migration will run on every RecordMessage
        // so it does need to be reasonably performant.
        // Instead, we use a regex to check for numeric literals.
        // Note that this does _not_ allow infinity/nan, even though protocol v1 _does_ allow them.
        // This is because JSON numeric literals don't allow those values.
        if (data.asText().matches("-?\\d+(\\.\\d+)?")) {
          // If this string is a numeric literal, convert it to a numeric node.
          return new DowngradedNode(Jsons.deserialize(data.asText()), true);
        } else {
          // Otherwise, just leave the node unchanged.
          return new DowngradedNode(data, false);
        }
      } else {
        // This is a non-numeric string (so could be a date/timestamp/etc)
        // Run it through the validator, but don't modify the data.
        return new DowngradedNode(data, validator.validate(schema, data).isEmpty());
      }
    } else {
      // Otherwise - the schema is invalid.
      return new DowngradedNode(data, false);
    }
  }

  /**
   * If data is an object, then we need to recursively downgrade all of its fields.
   */
  private DowngradedNode downgradeObjectNode(JsonNode data, JsonNode schema) {
    boolean isObjectSchema;
    // First, check whether the schema is supposed to be an object at all.
    if (schema.hasNonNull(REF_KEY)) {
      // If the schema uses a reference type, then it's not an object schema.
      isObjectSchema = false;
    } else if (schema.hasNonNull("type")) {
      // If the schema declares {type: object} or {type: [..., object, ...]}
      // Then this is an object schema
      JsonNode typeNode = schema.get("type");
      if (typeNode.isArray()) {
        isObjectSchema = false;
        for (JsonNode typeItem : typeNode) {
          if ("object".equals(typeItem.asText())) {
            isObjectSchema = true;
          }
        }
      } else {
        isObjectSchema = "object".equals(typeNode.asText());
      }
    } else {
      // If the schema doesn't declare a type at all (which is bad practice, but let's handle it anyway)
      // Then check for a properties entry, and assume that this is an object if it's present
      isObjectSchema = schema.hasNonNull("properties");
    }

    if (!isObjectSchema) {
      // If it's not supposed to be an object, then we can't do anything here.
      // Return the data without modification.
      return new DowngradedNode(data, false);
    } else {
      // If the schema _is_ for an object, then recurse into each field
      ObjectNode downgradedData = (ObjectNode) Jsons.emptyObject();
      JsonNode propertiesNode = schema.get("properties");

      Iterator<Entry<String, JsonNode>> dataFields = data.fields();
      boolean matchedSchema = true;
      while (dataFields.hasNext()) {
        Entry<String, JsonNode> field = dataFields.next();
        String key = field.getKey();
        JsonNode value = field.getValue();
        if (propertiesNode != null && propertiesNode.hasNonNull(key)) {
          // If we have a schema for this property, downgrade the value
          JsonNode subschema = propertiesNode.get(key);
          DowngradedNode downgradedNode = downgradeNode(value, subschema);
          downgradedData.set(key, downgradedNode.node);
          if (!downgradedNode.matchedSchema) {
            matchedSchema = false;
          }
        } else {
          // Else it's an additional property - we _could_ check additionalProperties,
          // but that's annoying. We don't actually respect that in destinations/normalization anyway.
          downgradedData.set(key, value);
        }
      }

      return new DowngradedNode(downgradedData, matchedSchema);
    }
  }

  /**
   * Much like objects, arrays must be recursively downgraded.
   */
  private DowngradedNode downgradeArrayNode(JsonNode data, JsonNode schema) {
    // Similar to objects, we first check whether this is even supposed to be an array.
    boolean isArraySchema;
    if (schema.hasNonNull(REF_KEY)) {
      // If the schema uses a reference type, then it's not an array schema.
      isArraySchema = false;
    } else if (schema.hasNonNull("type")) {
      // If the schema declares {type: array} or {type: [..., array, ...]}
      // Then this is an array schema
      JsonNode typeNode = schema.get("type");
      if (typeNode.isArray()) {
        isArraySchema = false;
        for (JsonNode typeItem : typeNode) {
          if ("array".equals(typeItem.asText())) {
            isArraySchema = true;
          }
        }
      } else {
        isArraySchema = "array".equals(typeNode.asText());
      }
    } else {
      // If the schema doesn't declare a type at all (which is bad practice, but let's handle it anyway)
      // Then check for an items entry, and assume that this is an array if it's present
      isArraySchema = schema.hasNonNull("items");
    }

    if (!isArraySchema) {
      return new DowngradedNode(data, false);
    } else {
      ArrayNode downgradedItems = Jsons.arrayNode();
      JsonNode itemsNode = schema.get("items");
      if (itemsNode == null) {
        // We _could_ check additionalItems, but much like the additionalProperties comment for objects:
        // it's a lot of work for no payoff
        return new DowngradedNode(data, true);
      } else if (itemsNode.isArray()) {
        // In the case of {items: [schema1, schema2, ...]}
        // We need to check schema1 against the first element of the array,
        // schema2 against the second element, etc.
        boolean allSchemasMatched = true;
        for (int i = 0; i < data.size(); i++) {
          JsonNode element = data.get(i);
          if (itemsNode.size() > i) {
            // If we have a schema for this element, then try downgrading the element
            DowngradedNode downgradedElement = downgradeNode(element, itemsNode.get(i));
            if (!downgradedElement.matchedSchema()) {
              allSchemasMatched = false;
            }
            downgradedItems.add(downgradedElement.node());
          }
        }
        // If there were more elements in `data` than there were schemas in `itemsNode`,
        // then just blindly add the rest of those elements.
        for (int i = itemsNode.size(); i < data.size(); i++) {
          downgradedItems.add(data.get(i));
        }
        return new DowngradedNode(downgradedItems, allSchemasMatched);
      } else {
        // IN the case of {items: schema}, we just check every array element against that schema.
        boolean matchedSchema = true;
        for (JsonNode item : data) {
          DowngradedNode downgradedNode = downgradeNode(item, itemsNode);
          downgradedItems.add(downgradedNode.node);
          if (!downgradedNode.matchedSchema) {
            matchedSchema = false;
          }
        }
        return new DowngradedNode(downgradedItems, matchedSchema);
      }
    }
  }

  @Override
  public Version getPreviousVersion() {
    return AirbyteProtocolVersion.V0;
  }

  @Override
  public Version getCurrentVersion() {
    return AirbyteProtocolVersion.V1;
  }

}
