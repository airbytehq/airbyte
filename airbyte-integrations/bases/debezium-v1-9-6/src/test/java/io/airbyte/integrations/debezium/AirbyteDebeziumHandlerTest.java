/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium;

import com.google.common.collect.Lists;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.List;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class AirbyteDebeziumHandlerTest {

  @Test
  public void shouldUseCdcTestShouldReturnTrue() {
    final AirbyteCatalog catalog = new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream(
            "MODELS_STREAM_NAME",
            "MODELS_SCHEMA",
            Field.of("COL_ID", JsonSchemaType.NUMBER),
            Field.of("COL_MAKE_ID", JsonSchemaType.NUMBER),
            Field.of("COL_MODEL", JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of("COL_ID")))));
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers
        .toDefaultConfiguredCatalog(catalog);
    // set all streams to incremental.
    configuredCatalog.getStreams().forEach(s -> s.setSyncMode(SyncMode.INCREMENTAL));

    Assertions.assertTrue(AirbyteDebeziumHandler.shouldUseCDC(configuredCatalog));
  }

  @Test
  public void shouldUseCdcTestShouldReturnFalse() {
    final AirbyteCatalog catalog = new AirbyteCatalog().withStreams(List.of(
        CatalogHelpers.createAirbyteStream(
            "MODELS_STREAM_NAME",
            "MODELS_SCHEMA",
            Field.of("COL_ID", JsonSchemaType.NUMBER),
            Field.of("COL_MAKE_ID", JsonSchemaType.NUMBER),
            Field.of("COL_MODEL", JsonSchemaType.STRING))
            .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
            .withSourceDefinedPrimaryKey(List.of(List.of("COL_ID")))));
    final ConfiguredAirbyteCatalog configuredCatalog = CatalogHelpers
        .toDefaultConfiguredCatalog(catalog);

    Assertions.assertFalse(AirbyteDebeziumHandler.shouldUseCDC(configuredCatalog));
  }

}
