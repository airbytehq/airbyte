/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.protocol.migrations.v1;

import static io.airbyte.protocol.models.JsonSchemaReferenceTypes.REF_KEY;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.node.TextNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.protocol.migrations.AirbyteMessageMigration;
import io.airbyte.commons.protocol.migrations.util.RecordMigrations;
import io.airbyte.commons.protocol.migrations.util.RecordMigrations.MigratedNode;
import io.airbyte.commons.version.AirbyteProtocolVersion;
import io.airbyte.commons.version.Version;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.JsonSchemaReferenceTypes;
import io.airbyte.validation.json.JsonSchemaValidator;
import jakarta.inject.Singleton;
import java.util.Iterator;
import java.util.Map.Entry;
import java.util.Objects;
import java.util.Optional;

@Singleton
public class AirbyteMessageMigrationV1 implements AirbyteMessageMigration<io.airbyte.protocol.models.v0.AirbyteMessage, AirbyteMessage> {

  private final JsonSchemaValidator validator;

  public AirbyteMessageMigrationV1() {
    this(new JsonSchemaValidator());
  }

  @VisibleForTesting
  public AirbyteMessageMigrationV1(final JsonSchemaValidator validator) {
    this.validator = validator;
  }

  @Override
  public io.airbyte.protocol.models.v0.AirbyteMessage downgrade(final AirbyteMessage oldMessage,
                                                                final Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog) {
    final io.airbyte.protocol.models.v0.AirbyteMessage newMessage = Jsons.object(
        Jsons.jsonNode(oldMessage),
        io.airbyte.protocol.models.v0.AirbyteMessage.class);
    if (oldMessage.getType() == Type.CATALOG && oldMessage.getCatalog() != null) {
      for (final io.airbyte.protocol.models.v0.AirbyteStream stream : newMessage.getCatalog().getStreams()) {
        final JsonNode schema = stream.getJsonSchema();
        SchemaMigrationV1.downgradeSchema(schema);
      }
    } else if (oldMessage.getType() == Type.RECORD && oldMessage.getRecord() != null) {
      if (configuredAirbyteCatalog.isPresent()) {
        final ConfiguredAirbyteCatalog catalog = configuredAirbyteCatalog.get();
        final io.airbyte.protocol.models.v0.AirbyteRecordMessage record = newMessage.getRecord();
        final Optional<ConfiguredAirbyteStream> maybeStream = catalog.getStreams().stream()
            .filter(stream -> Objects.equals(stream.getStream().getName(), record.getStream())
                && Objects.equals(stream.getStream().getNamespace(), record.getNamespace()))
            .findFirst();
        // If this record doesn't belong to any configured stream, then there's no point downgrading it
        // So only do the downgrade if we can find its stream
        if (maybeStream.isPresent()) {
          final JsonNode schema = maybeStream.get().getStream().getJsonSchema();
          final JsonNode oldData = record.getData();
          final MigratedNode downgradedNode = downgradeRecord(oldData, schema);
          record.setData(downgradedNode.node());
        }
      }
    }
    return newMessage;
  }

  @Override
  public AirbyteMessage upgrade(final io.airbyte.protocol.models.v0.AirbyteMessage oldMessage,
                                final Optional<ConfiguredAirbyteCatalog> configuredAirbyteCatalog) {
    // We're not introducing any changes to the structure of the record/catalog
    // so just clone a new message object, which we can edit in-place
    final AirbyteMessage newMessage = Jsons.object(
        Jsons.jsonNode(oldMessage),
        AirbyteMessage.class);
    if (oldMessage.getType() == io.airbyte.protocol.models.v0.AirbyteMessage.Type.CATALOG && oldMessage.getCatalog() != null) {
      for (final AirbyteStream stream : newMessage.getCatalog().getStreams()) {
        final JsonNode schema = stream.getJsonSchema();
        SchemaMigrationV1.upgradeSchema(schema);
      }
    } else if (oldMessage.getType() == io.airbyte.protocol.models.v0.AirbyteMessage.Type.RECORD && oldMessage.getRecord() != null) {
      final JsonNode oldData = newMessage.getRecord().getData();
      final JsonNode newData = upgradeRecord(oldData);
      newMessage.getRecord().setData(newData);
    }
    return newMessage;
  }

  /**
   * Returns a copy of oldData, with numeric values converted to strings. String and boolean values
   * are returned as-is for convenience, i.e. this is not a true deep copy.
   */
  private static JsonNode upgradeRecord(final JsonNode oldData) {
    if (oldData.isNumber()) {
      // Base case: convert numbers to strings
      return Jsons.convertValue(oldData.asText(), TextNode.class);
    } else if (oldData.isObject()) {
      // Recurse into each field of the object
      final ObjectNode newData = (ObjectNode) Jsons.emptyObject();

      final Iterator<Entry<String, JsonNode>> fieldsIterator = oldData.fields();
      while (fieldsIterator.hasNext()) {
        final Entry<String, JsonNode> next = fieldsIterator.next();
        final String key = next.getKey();
        final JsonNode value = next.getValue();

        final JsonNode newValue = upgradeRecord(value);
        newData.set(key, newValue);
      }

      return newData;
    } else if (oldData.isArray()) {
      // Recurse into each element of the array
      final ArrayNode newData = Jsons.arrayNode();
      for (final JsonNode element : oldData) {
        newData.add(upgradeRecord(element));
      }
      return newData;
    } else {
      // Base case: this is a string or boolean, so we don't need to modify it
      return oldData;
    }
  }

  /**
   * We need the schema to recognize which fields are integers, since it would be wrong to just assume
   * any numerical string should be parsed out.
   *
   * Works on a best-effort basis. If the schema doesn't match the data, we'll do our best to
   * downgrade anything that we can definitively say is a number. Should _not_ throw an exception if
   * bad things happen (e.g. we try to parse a non-numerical string as a number).
   */
  private MigratedNode downgradeRecord(final JsonNode data, final JsonNode schema) {
    return RecordMigrations.mutateDataNode(
        validator,
        s -> {
          if (s.hasNonNull(REF_KEY)) {
            final String type = s.get(REF_KEY).asText();
            return JsonSchemaReferenceTypes.INTEGER_REFERENCE.equals(type)
                || JsonSchemaReferenceTypes.NUMBER_REFERENCE.equals(type);
          } else {
            return false;
          }
        },
        (s, d) -> {
          if (d.asText().matches("-?\\d+(\\.\\d+)?")) {
            // If this string is a numeric literal, convert it to a numeric node.
            return new MigratedNode(Jsons.deserialize(d.asText()), true);
          } else {
            // Otherwise, just leave the node unchanged.
            return new MigratedNode(d, false);
          }
        },
        data, schema);
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
