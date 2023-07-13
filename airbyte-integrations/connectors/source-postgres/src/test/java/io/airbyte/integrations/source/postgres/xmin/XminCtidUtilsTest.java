/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.xmin;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.ctid.CtidUtils.StreamsCategorised;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.integrations.source.postgres.internal.models.InternalModels.StateType;
import io.airbyte.integrations.source.postgres.internal.models.XminStatus;
import io.airbyte.integrations.source.postgres.xmin.XminCtidUtils.XminStreams;
import io.airbyte.integrations.source.relationaldb.state.StreamStateManager;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.CatalogHelpers;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import org.junit.jupiter.api.Test;

public class XminCtidUtilsTest {

  private static final ConfiguredAirbyteStream MODELS_STREAM = CatalogHelpers.toDefaultConfiguredStream(CatalogHelpers.createAirbyteStream(
      "MODELS_STREAM_NAME",
      "MODELS_SCHEMA",
      Field.of("COL_ID", JsonSchemaType.INTEGER),
      Field.of("COL_MAKE_ID", JsonSchemaType.INTEGER),
      Field.of("COL_MODEL", JsonSchemaType.STRING))
      .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
      .withSourceDefinedPrimaryKey(List.of(List.of("COL_ID"))))
      .withSyncMode(SyncMode.INCREMENTAL);

  private static final ConfiguredAirbyteStream MODELS_STREAM_2 = CatalogHelpers.toDefaultConfiguredStream(CatalogHelpers.createAirbyteStream(
      "MODELS_STREAM_NAME_2",
      "MODELS_SCHEMA",
      Field.of("COL_ID", JsonSchemaType.INTEGER),
      Field.of("COL_MAKE_ID", JsonSchemaType.INTEGER),
      Field.of("COL_MODEL", JsonSchemaType.STRING))
      .withSupportedSyncModes(Lists.newArrayList(SyncMode.FULL_REFRESH, SyncMode.INCREMENTAL))
      .withSourceDefinedPrimaryKey(List.of(List.of("COL_ID"))))
      .withSyncMode(SyncMode.INCREMENTAL);

  @Test
  public void emptyStateTest() {
    final ConfiguredAirbyteCatalog configuredCatalog = new ConfiguredAirbyteCatalog().withStreams(Arrays.asList(MODELS_STREAM, MODELS_STREAM_2));
    final XminStatus xminStatus = new XminStatus().withStateType(StateType.XMIN).withVersion(2L).withXminXidValue(9L).withXminRawValue(9L)
        .withNumWraparound(1L);
    final StreamStateManager streamStateManager = new StreamStateManager(Collections.emptyList(), configuredCatalog);
    final StreamsCategorised<XminStreams> streamsCategorised = XminCtidUtils.categoriseStreams(streamStateManager, configuredCatalog, xminStatus);

    assertTrue(streamsCategorised.remainingStreams().streamsForXminSync().isEmpty());
    assertTrue(streamsCategorised.remainingStreams().statesFromXminSync().isEmpty());

    assertEquals(2, streamsCategorised.ctidStreams().streamsForCtidSync().size());
    assertThat(streamsCategorised.ctidStreams().streamsForCtidSync()).containsExactlyInAnyOrder(MODELS_STREAM, MODELS_STREAM_2);
    assertTrue(streamsCategorised.ctidStreams().statesFromCtidSync().isEmpty());
  }

  @Test
  public void correctCategorisationTest() {
    final ConfiguredAirbyteCatalog configuredCatalog = new ConfiguredAirbyteCatalog().withStreams(Arrays.asList(MODELS_STREAM, MODELS_STREAM_2));
    final XminStatus xminStatus = new XminStatus().withStateType(StateType.XMIN).withVersion(2L).withXminXidValue(9L).withXminRawValue(9L)
        .withNumWraparound(1L);
    final JsonNode xminStatusAsJson = Jsons.jsonNode(xminStatus);
    final AirbyteStateMessage xminState = generateStateMessage(xminStatusAsJson,
        new StreamDescriptor().withName(MODELS_STREAM.getStream().getName()).withNamespace(MODELS_STREAM.getStream().getNamespace()));

    final CtidStatus ctidStatus = new CtidStatus().withStateType(StateType.CTID).withVersion(2L).withCtid("123").withRelationFilenode(456L)
        .withIncrementalState(xminStatusAsJson);
    final JsonNode ctidStatusAsJson = Jsons.jsonNode(ctidStatus);
    final AirbyteStateMessage ctidState = generateStateMessage(ctidStatusAsJson,
        new StreamDescriptor().withName(MODELS_STREAM_2.getStream().getName()).withNamespace(MODELS_STREAM_2.getStream().getNamespace()));

    final StreamStateManager streamStateManager = new StreamStateManager(Arrays.asList(xminState, ctidState), configuredCatalog);
    final StreamsCategorised<XminStreams> streamsCategorised = XminCtidUtils.categoriseStreams(streamStateManager, configuredCatalog, xminStatus);

    assertEquals(1, streamsCategorised.remainingStreams().streamsForXminSync().size());
    assertEquals(MODELS_STREAM, streamsCategorised.remainingStreams().streamsForXminSync().get(0));
    assertEquals(1, streamsCategorised.remainingStreams().statesFromXminSync().size());
    assertEquals(xminState, streamsCategorised.remainingStreams().statesFromXminSync().get(0));

    assertEquals(1, streamsCategorised.ctidStreams().streamsForCtidSync().size());
    assertEquals(MODELS_STREAM_2, streamsCategorised.ctidStreams().streamsForCtidSync().get(0));
    assertEquals(1, streamsCategorised.ctidStreams().statesFromCtidSync().size());
    assertEquals(ctidState, streamsCategorised.ctidStreams().statesFromCtidSync().get(0));
  }

  private AirbyteStateMessage generateStateMessage(final JsonNode stateData, final StreamDescriptor streamDescriptor) {
    return new AirbyteStateMessage().withType(AirbyteStateType.STREAM)
        .withStream(new AirbyteStreamState().withStreamDescriptor(streamDescriptor).withStreamState(stateData));
  }

}
