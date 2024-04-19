/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.cdk.integrations.source.relationaldb.models.CdcState;
import io.airbyte.cdk.integrations.source.relationaldb.models.DbStreamState;
import io.airbyte.cdk.integrations.source.relationaldb.models.OrderedColumnLoadStatus;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil.InitialLoadStreams;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil.OrderedColumnInfo;
import io.airbyte.protocol.models.v0.*;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import org.jetbrains.annotations.Nullable;

import java.util.*;
import java.util.function.Function;
import java.util.stream.Collectors;

public class MssqlInitialLoadGlobalStateManager extends MssqlInitialLoadStateManager {

  private final Map<AirbyteStreamNameNamespacePair, OrderedColumnInfo> pairToOrderedColInfo;
  protected final CdcState cdcState;

  // Only one global state is emitted, which is fanned out into many entries in the DB by platform. As
  // a result, we need to keep track of streams that have completed the snapshot.
  private Set<AirbyteStreamNameNamespacePair> streamsThatHaveCompletedSnapshot;

  // No special handling for resumable full refresh streams. We will report the cursor as it is.
  private Set<AirbyteStreamNameNamespacePair> resumableFullRefreshStreams;

  public MssqlInitialLoadGlobalStateManager(final InitialLoadStreams initialLoadStreams,
                                            final Map<AirbyteStreamNameNamespacePair, OrderedColumnInfo> pairToOrderedColInfo,
                                            final CdcState cdcState,
                                            final ConfiguredAirbyteCatalog catalog) {
    this.cdcState = cdcState;
    this.pairToOrderedColLoadStatus = MssqlInitialLoadStateManager.initPairToOrderedColumnLoadStatusMap(initialLoadStreams.pairToInitialLoadStatus());
    this.pairToOrderedColInfo = pairToOrderedColInfo;
    initStreams(initialLoadStreams, catalog);
  }

  private void initStreams(final InitialLoadStreams initialLoadStreams,
                           final ConfiguredAirbyteCatalog catalog) {
    this.streamsThatHaveCompletedSnapshot = new HashSet<>();
    this.resumableFullRefreshStreams = new HashSet<>();
    catalog.getStreams().forEach(configuredAirbyteStream -> {
      if (!initialLoadStreams.streamsForInitialLoad().contains(configuredAirbyteStream)
      && configuredAirbyteStream.getSyncMode() == SyncMode.INCREMENTAL) {
        this.streamsThatHaveCompletedSnapshot.add(
                new AirbyteStreamNameNamespacePair(configuredAirbyteStream.getStream().getName(), configuredAirbyteStream.getStream().getNamespace()));
      }
      if (initialLoadStreams.streamsForInitialLoad().contains(configuredAirbyteStream)
      && configuredAirbyteStream.getSyncMode() == SyncMode.FULL_REFRESH) {
        this.resumableFullRefreshStreams.add(
                new AirbyteStreamNameNamespacePair(configuredAirbyteStream.getStream().getName(), configuredAirbyteStream.getStream().getNamespace()));
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
      streamStates.add(getAirbyteStreamState(stream, Jsons.jsonNode(ocStatus)));
    });

    if (airbyteStream.getSyncMode() == SyncMode.INCREMENTAL) {
      AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(airbyteStream.getStream().getName(), airbyteStream.getStream().getNamespace());
      var ocStatus = getOrderedColumnLoadStatus(pair);
      streamStates.add(getAirbyteStreamState(pair, Jsons.jsonNode(ocStatus)));
    }

    final AirbyteGlobalState globalState = new AirbyteGlobalState();
    globalState.setSharedState(Jsons.jsonNode(cdcState));
    globalState.setStreamStates(streamStates);

    return new AirbyteStateMessage()
            .withType(AirbyteStateType.GLOBAL)
            .withGlobal(globalState);
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
      io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair pair = new io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair(airbyteStream.getStream().getName(), airbyteStream.getStream().getNamespace());
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

    final AirbyteGlobalState globalState = new AirbyteGlobalState();
    globalState.setSharedState(Jsons.jsonNode(cdcState));
    globalState.setStreamStates(streamStates);

    return new AirbyteStateMessage()
            .withType(AirbyteStateType.GLOBAL)
            .withGlobal(globalState);
  }

  @Override
  public OrderedColumnInfo getOrderedColumnInfo(final AirbyteStreamNameNamespacePair pair) {
    return pairToOrderedColInfo.get(pair);
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
