/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState;
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.postgres.cdc.PostgresCdcCtidUtils.CtidStreams;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CtidGlobalStateManager extends CtidStateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(CtidGlobalStateManager.class);

  private final StateManager stateManager;
  private Set<AirbyteStreamNameNamespacePair> resumableFullRefreshStreams;
  private Set<AirbyteStreamNameNamespacePair> nonResumableFullRefreshStreams;
  private Set<AirbyteStreamNameNamespacePair> streamsThatHaveCompletedSnapshot;
  private final boolean savedOffsetAfterReplicationSlotLSN;
  private final CdcState defaultCdcState;

  public CtidGlobalStateManager(final CtidStreams ctidStreams,
                                final FileNodeHandler fileNodeHandler,
                                final StateManager stateManager,
                                final ConfiguredAirbyteCatalog catalog,
                                final boolean savedOffsetAfterReplicationSlotLSN,
                                final CdcState defaultCdcState) {
    super(filterOutExpiredFileNodes(ctidStreams.pairToCtidStatus(), fileNodeHandler));
    this.stateManager = stateManager;
    this.savedOffsetAfterReplicationSlotLSN = savedOffsetAfterReplicationSlotLSN;
    this.defaultCdcState = defaultCdcState;
    this.fileNodeHandler = fileNodeHandler;
    initStream(ctidStreams, catalog);
  }

  private void initStream(final CtidStreams ctidStreams,
                          final ConfiguredAirbyteCatalog catalog) {
    this.streamsThatHaveCompletedSnapshot = new HashSet<>();
    this.resumableFullRefreshStreams = new HashSet<>();
    this.nonResumableFullRefreshStreams = new HashSet<>();
    catalog.getStreams().forEach(configuredAirbyteStream -> {
      var pair =
          new AirbyteStreamNameNamespacePair(configuredAirbyteStream.getStream().getName(), configuredAirbyteStream.getStream().getNamespace());
      if (!ctidStreams.streamsForCtidSync().contains(configuredAirbyteStream) && configuredAirbyteStream.getSyncMode() == SyncMode.INCREMENTAL) {
        streamsThatHaveCompletedSnapshot.add(pair);
      }

      if (configuredAirbyteStream.getSyncMode() == SyncMode.FULL_REFRESH) {
        // Note some streams still do not have `isResumable` field set.
        if (configuredAirbyteStream.getStream().getIsResumable() != null && configuredAirbyteStream.getStream().getIsResumable()) {
          this.resumableFullRefreshStreams.add(pair);
        } else if (fileNodeHandler.hasFileNode(
            new AirbyteStreamNameNamespacePair(configuredAirbyteStream.getStream().getName(), configuredAirbyteStream.getStream().getNamespace()))) {
          this.resumableFullRefreshStreams.add(pair);
        } else {
          this.nonResumableFullRefreshStreams.add(pair);
        }
      }
    });
  }

  private static Map<AirbyteStreamNameNamespacePair, CtidStatus> filterOutExpiredFileNodes(
                                                                                           final Map<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair, CtidStatus> pairToCtidStatus,
                                                                                           final FileNodeHandler fileNodeHandler) {
    final Map<AirbyteStreamNameNamespacePair, CtidStatus> filteredMap = new HashMap<>();
    pairToCtidStatus.forEach((pair, ctidStatus) -> {
      final AirbyteStreamNameNamespacePair updatedPair = new AirbyteStreamNameNamespacePair(pair.getName(), pair.getNamespace());
      if (validateRelationFileNode(ctidStatus, updatedPair, fileNodeHandler)) {
        filteredMap.put(updatedPair, ctidStatus);
      } else {
        LOGGER.warn(
            "The relation file node for table in source db {} is not equal to the saved ctid state, a full sync from scratch will be triggered.",
            pair);
      }
    });
    return filteredMap;
  }

  @Override
  public AirbyteStateMessage createCtidStateMessage(final AirbyteStreamNameNamespacePair pair, final CtidStatus ctidStatus) {
    pairToCtidStatus.put(pair, ctidStatus);
    final List<AirbyteStreamState> streamStates = new ArrayList<>();

    streamsThatHaveCompletedSnapshot.forEach(stream -> {
      final DbStreamState state = getFinalState(stream);
      streamStates.add(getAirbyteStreamState(stream, Jsons.jsonNode(state)));
    });

    resumableFullRefreshStreams.forEach(stream -> {
      if (getCtidStatus(new AirbyteStreamNameNamespacePair(stream.getName(), stream.getNamespace())) != null) {
        final CtidStatus ctidStatusForFullRefreshStream = generateCtidStatusForState(stream);
        streamStates.add(getAirbyteStreamState(stream, (Jsons.jsonNode(ctidStatusForFullRefreshStream))));
      }
    });

    nonResumableFullRefreshStreams.forEach(stream -> {
      streamStates.add(new AirbyteStreamState()
          .withStreamDescriptor(
              new StreamDescriptor().withName(stream.getName()).withNamespace(stream.getNamespace())));
    });

    if (!resumableFullRefreshStreams.contains(pair) && !nonResumableFullRefreshStreams.contains(pair)) {
      streamStates.add(getAirbyteStreamState(pair, (Jsons.jsonNode(ctidStatus))));
    }

    return new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(generateGlobalState(streamStates));
  }

  public AirbyteGlobalState generateGlobalState(final List<AirbyteStreamState> streamStates) {
    final CdcState stateToBeUsed = getCdcState();
    final AirbyteGlobalState globalState = new AirbyteGlobalState();
    globalState.setSharedState(Jsons.jsonNode(stateToBeUsed));
    globalState.setStreamStates(streamStates);
    return globalState;

  }

  public CdcState getCdcState() {
    final CdcState stateManagerCdcState = stateManager.getCdcStateManager().getCdcState();

    return !savedOffsetAfterReplicationSlotLSN || stateManagerCdcState == null
        || stateManagerCdcState.getState() == null ? defaultCdcState
            : stateManagerCdcState;

  }

  private boolean isIncrementalStream(final AirbyteStreamNameNamespacePair pair) {
    return !resumableFullRefreshStreams.contains(pair) && !nonResumableFullRefreshStreams.contains(pair);
  }

  @Override
  public AirbyteStateMessage createFinalStateMessage(final AirbyteStreamNameNamespacePair pair, final JsonNode streamStateForIncrementalRun) {
    // Only incremental streams can be transformed into the next phase.
    if (isIncrementalStream(pair)) {
      streamsThatHaveCompletedSnapshot.add(pair);
    }

    if (resumableFullRefreshStreams.contains(pair)) {
      final CtidStatus ctidStatusForFullRefreshStream = generateCtidStatusForState(pair);
      pairToCtidStatus.put(pair, ctidStatusForFullRefreshStream);
    }

    final List<AirbyteStreamState> streamStates = new ArrayList<>();
    streamsThatHaveCompletedSnapshot.forEach(stream -> {
      final DbStreamState state = getFinalState(stream);
      streamStates.add(getAirbyteStreamState(stream, Jsons.jsonNode(state)));
    });

    resumableFullRefreshStreams.forEach(stream -> {
      final CtidStatus ctidStatusForFullRefreshStream = generateCtidStatusForState(stream);
      streamStates.add(getAirbyteStreamState(stream, Jsons.jsonNode(ctidStatusForFullRefreshStream)));
    });

    nonResumableFullRefreshStreams.forEach(stream -> {
      streamStates.add(new AirbyteStreamState()
          .withStreamDescriptor(
              new StreamDescriptor().withName(stream.getName()).withNamespace(stream.getNamespace())));
    });

    return new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(generateGlobalState(streamStates));
  }

  private AirbyteStreamState getAirbyteStreamState(final AirbyteStreamNameNamespacePair pair, final JsonNode stateData) {
    assert Objects.nonNull(pair);
    assert Objects.nonNull(pair.getName());
    assert Objects.nonNull(pair.getNamespace());

    return new AirbyteStreamState()
        .withStreamDescriptor(
            new StreamDescriptor().withName(pair.getName()).withNamespace(pair.getNamespace()))
        .withStreamState(stateData);
  }

  private DbStreamState getFinalState(final AirbyteStreamNameNamespacePair pair) {
    assert Objects.nonNull(pair);
    assert Objects.nonNull(pair.getName());
    assert Objects.nonNull(pair.getNamespace());

    return new DbStreamState()
        .withStreamName(pair.getName())
        .withStreamNamespace(pair.getNamespace())
        .withCursorField(Collections.emptyList())
        .withCursor(null);
  }

}
