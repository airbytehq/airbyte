/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mongodb.cdc.MongoDbCdcConnectorMetadataInjector;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Collection of utility methods for generating the {@link AirbyteCatalog}.
 */
public class MongoCatalogHelper {

  /**
   * The default cursor field name.
   */
  public static final String DEFAULT_CURSOR_FIELD = MongoDbCdcConnectorMetadataInjector.CDC_DEFAULT_CURSOR;

  /**
   * The default primary key field name.
   */
  public static final String DEFAULT_PRIMARY_KEY = MongoConstants.ID_FIELD;

  /**
   * The list of supported sync modes for a given stream.
   */
  public static final List<SyncMode> SUPPORTED_SYNC_MODES = List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL);

  /**
   * Name of the property in the JSON representation of an Airbyte stream that contains the discovered
   * fields.
   */
  public static final String AIRBYTE_STREAM_PROPERTIES = "properties";

  /**
   * Builds an {@link AirbyteStream} with the correct configuration for this source.
   *
   * @param streamName The name of the stream.
   * @param streamNamespace The namespace of the stream.
   * @param fields The fields associated with the stream.
   * @return The configured {@link AirbyteStream} for this source.
   */
  public static AirbyteStream buildAirbyteStream(final String streamName, final String streamNamespace, final List<Field> fields) {
    return addCdcMetadataColumns(CatalogHelpers.createAirbyteStream(streamName, streamNamespace, fields)
        .withSupportedSyncModes(SUPPORTED_SYNC_MODES)
        .withSourceDefinedCursor(true)
        .withDefaultCursorField(List.of(DEFAULT_CURSOR_FIELD))
        .withSourceDefinedPrimaryKey(List.of(List.of(DEFAULT_PRIMARY_KEY))));
  }

  /**
   * Builds an {@link AirbyteStream} with the correct configuration for this source, in schemaless
   * mode. All fields are stripped out and the only fields kept are _id, _data, and the CDC fields.
   *
   * @param streamName The name of the stream.
   * @param streamNamespace The namespace of the stream.
   * @param fields The fields associated with the stream.
   * @return The configured {@link AirbyteStream} for this source.
   */
  public static AirbyteStream buildSchemalessAirbyteStream(final String streamName, final String streamNamespace, final List<Field> fields) {
    // The packed airbyte catalog should only contain the _id field.
    final List<Field> idFieldList = fields.stream().filter(field -> field.getName().equals(MongoConstants.ID_FIELD)).collect(Collectors.toList());
    return addDataMetadataColumn(buildAirbyteStream(streamName, streamNamespace, idFieldList));
  }

  /**
   * Adds CDC metadata columns to the stream.
   *
   * @param stream An {@link AirbyteStream}.
   * @return The modified {@link AirbyteStream}.
   */
  private static AirbyteStream addCdcMetadataColumns(final AirbyteStream stream) {
    final ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    final ObjectNode properties = (ObjectNode) jsonSchema.get(AIRBYTE_STREAM_PROPERTIES);
    MongoDbCdcConnectorMetadataInjector.addCdcMetadataColumns(properties);
    return stream;
  }

  /**
   * Adds the data metadata columns to the stream, for schemaless (packed) mode.
   *
   * @param stream An {@link AirbyteStream}.
   * @return The modified {@link AirbyteStream}.
   */
  private static AirbyteStream addDataMetadataColumn(final AirbyteStream stream) {
    final ObjectNode jsonSchema = (ObjectNode) stream.getJsonSchema();
    final ObjectNode properties = (ObjectNode) jsonSchema.get(AIRBYTE_STREAM_PROPERTIES);
    addSchemalessModeDataColumn(properties);
    return stream;
  }

  private static ObjectNode addSchemalessModeDataColumn(final ObjectNode properties) {
    final JsonNode objectType = Jsons.jsonNode(ImmutableMap.of("type", "object"));
    properties.set(MongoConstants.SCHEMALESS_MODE_DATA_FIELD, objectType);
    return properties;
  }

}
