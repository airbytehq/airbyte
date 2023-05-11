/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.helper;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.google.common.collect.Lists;
import io.airbyte.commons.text.Names;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.protocol.models.AirbyteStream;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.SyncMode;
import java.util.Collections;
import java.util.List;
import org.junit.jupiter.api.Test;

class CatalogClientConvertersTest {

  public static final String ID_FIELD_NAME = "id";
  private static final String STREAM_NAME = "users-data";
  private static final AirbyteStream STREAM = new AirbyteStream()
      .withName(STREAM_NAME)
      .withJsonSchema(
          CatalogHelpers.fieldsToJsonSchema(Field.of(ID_FIELD_NAME, JsonSchemaType.STRING)))
      .withDefaultCursorField(Lists.newArrayList(ID_FIELD_NAME))
      .withSourceDefinedCursor(false)
      .withSourceDefinedPrimaryKey(Collections.emptyList())
      .withSupportedSyncModes(List.of(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL));

  private static final io.airbyte.api.client.model.generated.AirbyteStream CLIENT_STREAM =
      new io.airbyte.api.client.model.generated.AirbyteStream()
          .name(STREAM_NAME)
          .jsonSchema(CatalogHelpers.fieldsToJsonSchema(Field.of(ID_FIELD_NAME, JsonSchemaType.STRING)))
          .defaultCursorField(Lists.newArrayList(ID_FIELD_NAME))
          .sourceDefinedCursor(false)
          .sourceDefinedPrimaryKey(Collections.emptyList())
          .supportedSyncModes(List.of(io.airbyte.api.client.model.generated.SyncMode.FULL_REFRESH,
              io.airbyte.api.client.model.generated.SyncMode.INCREMENTAL));
  private static final io.airbyte.api.client.model.generated.AirbyteStreamConfiguration CLIENT_DEFAULT_STREAM_CONFIGURATION =
      new io.airbyte.api.client.model.generated.AirbyteStreamConfiguration()
          .syncMode(io.airbyte.api.client.model.generated.SyncMode.FULL_REFRESH)
          .cursorField(Lists.newArrayList(ID_FIELD_NAME))
          .destinationSyncMode(io.airbyte.api.client.model.generated.DestinationSyncMode.APPEND)
          .primaryKey(Collections.emptyList())
          .aliasName(Names.toAlphanumericAndUnderscore(STREAM_NAME))
          .selected(true);

  private static final AirbyteCatalog BASIC_MODEL_CATALOG = new AirbyteCatalog().withStreams(
      Lists.newArrayList(STREAM));

  private static final io.airbyte.api.client.model.generated.AirbyteCatalog EXPECTED_CLIENT_CATALOG =
      new io.airbyte.api.client.model.generated.AirbyteCatalog()
          .streams(Lists.newArrayList(
              new io.airbyte.api.client.model.generated.AirbyteStreamAndConfiguration()
                  .stream(CLIENT_STREAM)
                  .config(CLIENT_DEFAULT_STREAM_CONFIGURATION)));

  @Test
  void testConvertToClientAPI() {
    assertEquals(EXPECTED_CLIENT_CATALOG,
        CatalogClientConverters.toAirbyteCatalogClientApi(BASIC_MODEL_CATALOG));
  }

  @Test
  void testConvertToProtocol() {
    assertEquals(BASIC_MODEL_CATALOG,
        CatalogClientConverters.toAirbyteProtocol(EXPECTED_CLIENT_CATALOG));
  }

}
