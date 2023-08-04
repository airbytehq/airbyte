/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal;

import io.airbyte.integrations.debezium.internals.DebeziumEventUtils;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.List;

/**
 * Collection of utility methods for generating the {@link AirbyteCatalog}.
 */
public class MongoCatalogHelper {

  /**
   * The default cursor field name.
   */
  public static final String DEFAULT_CURSOR_FIELD = "_id";

  /**
   * The list of supported sync modes for a given stream.
   */
  public static final List<SyncMode> SUPPORTED_SYNC_MODES = List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL);

  /**
   * Builds an {@link AirbyteStream} with the correct configuration for this source.
   *
   * @param streamName The name of the stream.
   * @param streamNamespace The namespace of the stream.
   * @param fields The fields associated with the stream.
   * @return The configured {@link AirbyteStream} for this source.
   */
  public static AirbyteStream buildAirbyteStream(final String streamName, final String streamNamespace, final List<Field> fields) {
    return CatalogHelpers.createAirbyteStream(streamName, streamNamespace, addCdcMetadataColumns(fields))
        .withSupportedSyncModes(SUPPORTED_SYNC_MODES)
        .withSourceDefinedCursor(true)
        .withDefaultCursorField(List.of(DEFAULT_CURSOR_FIELD))
        .withSourceDefinedPrimaryKey(List.of(List.of(DEFAULT_CURSOR_FIELD)));
  }

  /**
   * Adds the metadata columns required to use CDC to the list of discovered fields.
   *
   * @param fields The list of discovered fields.
   * @return The modified list of discovered fields that includes the required CDC metadata columns.
   */
  public static List<Field> addCdcMetadataColumns(final List<Field> fields) {
    final List<Field> modifiedFields = new ArrayList<>(fields);
    modifiedFields.add(new Field(DebeziumEventUtils.CDC_LSN, JsonSchemaType.NUMBER));
    modifiedFields.add(new Field(DebeziumEventUtils.CDC_UPDATED_AT, JsonSchemaType.STRING));
    modifiedFields.add(new Field(DebeziumEventUtils.CDC_DELETED_AT, JsonSchemaType.STRING));
    return modifiedFields;
  }

}
