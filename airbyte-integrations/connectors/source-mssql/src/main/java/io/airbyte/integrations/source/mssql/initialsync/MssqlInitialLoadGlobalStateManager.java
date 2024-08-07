/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState;
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateManager;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil.InitialLoadStreams;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil.OrderedColumnInfo;
import io.airbyte.protocol.models.v0.*;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import java.util.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MssqlInitialLoadGlobalStateManager extends MssqlInitialLoadStateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlInitialLoadGlobalStateManager.class);
  private StateManager stateManager;
  private final CdcState initialCdcState;
  // Only one global state is emitted, which is fanned out into many entries in the DB by platform. As
  // a result, we need to keep track of streams that have completed the snapshot.
  private Set<AirbyteStreamNameNamespacePair> streamsThatHaveCompletedSnapshot;

  // No special handling for resumable full refresh streams. We will report the cursor as it is.
  private Set<AirbyteStreamNameNamespacePair> resumableFullRefreshStreams;
  private Set<AirbyteStreamNameNamespacePair> nonResumableFullRefreshStreams;

  public MssqlInitialLoadGlobalStateManager(final InitialLoadStreams initialLoadStreams,
                                            final Map<AirbyteStreamNameNamespacePair, OrderedColumnInfo> pairToOrderedColInfo,
                                            final StateManager stateManager,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final CdcState initialCdcState) {
    this.pairToOrderedColLoadStatus = MssqlInitialLoadStateManager.initPairToOrderedColumnLoadStatusMap(initialLoadStreams.pairToInitialLoadStatus());
    this.pairToOrderedColInfo = pairToOrderedColInfo;
    this.stateManager = stateManager;
    this.initialCdcState = initialCdcState;
    this.streamStateForIncrementalRunSupplier = pair -> Jsons.emptyObject();
    initStreams(initialLoadStreams, catalog);
  }

  private AirbyteGlobalState generateGlobalState(final List<AirbyteStreamState> streamStates) {
    CdcState cdcState = stateManager.getCdcStateManager().getCdcState();
    if (cdcState == null || cdcState.getState() == null) {
      cdcState = initialCdcState;
    }

    final AirbyteGlobalState globalState = new AirbyteGlobalState();
    globalState.setSharedState(Jsons.jsonNode(cdcState));
    globalState.setStreamStates(streamStates);
    return globalState;
  }

  private void initStreams(final InitialLoadStreams initialLoadStreams,
                           final ConfiguredAirbyteCatalog catalog) {
    this.streamsThatHaveCompletedSnapshot = new HashSet<>();
    this.resumableFullRefreshStreams = new HashSet<>();
    this.nonResumableFullRefreshStreams = new HashSet<>();

    catalog.getStreams().forEach(configuredAirbyteStream -> {
      var pairInStream =
          new AirbyteStreamNameNamespacePair(configuredAirbyteStream.getStream().getName(), configuredAirbyteStream.getStream().getNamespace());
      if (!initialLoadStreams.streamsForInitialLoad().contains(configuredAirbyteStream)
          && configuredAirbyteStream.getSyncMode() == SyncMode.INCREMENTAL) {
        this.streamsThatHaveCompletedSnapshot.add(pairInStream);
      }
      if (configuredAirbyteStream.getSyncMode() == SyncMode.FULL_REFRESH) {
        if (initialLoadStreams.streamsForInitialLoad().contains(configuredAirbyteStream)) {
          this.resumableFullRefreshStreams.add(pairInStream);
        } else {
          this.nonResumableFullRefreshStreams.add(pairInStream);
        }
      }
    });
  }

  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint(final ConfiguredAirbyteStream airbyteStream) {
    final List<AirbyteStreamState> streamStates = new ArrayList<>();
    streamsThatHaveCompletedSnapshot.forEach(stream -> {
      final DbStreamState state = getFinalState(stream);
      streamStates.add(getAirbyteStreamState(stream, Jsons.jsonNode(state)));
    });

    resumableFullRefreshStreams.forEach(stream -> {
      var ocStatus = getOrderedColumnLoadStatus(stream);
      if (ocStatus != null) {
        streamStates.add(getAirbyteStreamState(stream, Jsons.jsonNode(ocStatus)));
      }
    });

    if (airbyteStream.getSyncMode() == SyncMode.INCREMENTAL) {
      AirbyteStreamNameNamespacePair pair =
          new AirbyteStreamNameNamespacePair(airbyteStream.getStream().getName(), airbyteStream.getStream().getNamespace());
      var ocStatus = getOrderedColumnLoadStatus(pair);
      streamStates.add(getAirbyteStreamState(pair, Jsons.jsonNode(ocStatus)));
    }

    return new AirbyteStateMessage()
        .withType(AirbyteStateType.GLOBAL)
        .withGlobal(generateGlobalState(streamStates));
  }

  private AirbyteStreamState getAirbyteStreamState(final AirbyteStreamNameNamespacePair pair, final JsonNode stateData) {
    Preconditions.checkNotNull(pair);
    Preconditions.checkNotNull(pair.getName());
    Preconditions.checkNotNull(pair.getNamespace());

    return new AirbyteStreamState()
        .withStreamDescriptor(
            new StreamDescriptor().withName(pair.getName()).withNamespace(pair.getNamespace()))
        .withStreamState(stateData);
  }

  @Override
  public AirbyteStateMessage createFinalStateMessage(final ConfiguredAirbyteStream airbyteStream) {
    if (airbyteStream.getSyncMode() == SyncMode.INCREMENTAL) {
      io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair pair = new io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair(
          airbyteStream.getStream().getName(), airbyteStream.getStream().getNamespace());
      streamsThatHaveCompletedSnapshot.add(pair);
    }
    final List<AirbyteStreamState> streamStates = new ArrayList<>();
    streamsThatHaveCompletedSnapshot.forEach(stream -> {
      final DbStreamState state = getFinalState(stream);
      streamStates.add(getAirbyteStreamState(stream, Jsons.jsonNode(state)));
    });

    resumableFullRefreshStreams.forEach(stream -> {
      var ocStatus = getOrderedColumnLoadStatus(stream);
      streamStates.add(getAirbyteStreamState(stream, Jsons.jsonNode(ocStatus)));
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

  private DbStreamState getFinalState(final AirbyteStreamNameNamespacePair pair) {
    Preconditions.checkNotNull(pair);
    Preconditions.checkNotNull(pair.getName());
    Preconditions.checkNotNull(pair.getNamespace());

    return new DbStreamState()
        .withStreamName(pair.getName())
        .withStreamNamespace(pair.getNamespace())
        .withCursorField(Collections.emptyList())
        .withCursor(null);
  }

}
