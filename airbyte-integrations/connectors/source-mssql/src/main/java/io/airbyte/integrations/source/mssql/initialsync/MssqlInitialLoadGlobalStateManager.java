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
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteGlobalState;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.function.Function;
import java.util.stream.Collectors;

public class MssqlInitialLoadGlobalStateManager extends MssqlInitialLoadStateManager {

  private final Map<AirbyteStreamNameNamespacePair, OrderedColumnInfo> pairToOrderedColInfo;
  private final CdcState cdcState;

  // Only one global state is emitted, which is fanned out into many entries in the DB by platform. As
  // a result, we need to keep track of streams that have completed the snapshot.
  private final Set<AirbyteStreamNameNamespacePair> streamsThatHaveCompletedSnapshot;

  public MssqlInitialLoadGlobalStateManager(final InitialLoadStreams initialLoadStreams,
                                            final Map<AirbyteStreamNameNamespacePair, OrderedColumnInfo> pairToOrderedColInfo,
                                            final CdcState cdcState,
                                            final ConfiguredAirbyteCatalog catalog,
                                            final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier) {
    this.cdcState = cdcState;
    this.pairToOrderedColLoadStatus = MssqlInitialLoadStateManager.initPairToOrderedColumnLoadStatusMap(initialLoadStreams.pairToInitialLoadStatus());
    this.pairToOrderedColInfo = pairToOrderedColInfo;
    this.streamsThatHaveCompletedSnapshot = initStreamsCompletedSnapshot(initialLoadStreams, catalog);
    this.streamStateForIncrementalRunSupplier = streamStateForIncrementalRunSupplier;
  }

  private static Set<AirbyteStreamNameNamespacePair> initStreamsCompletedSnapshot(final InitialLoadStreams initialLoadStreams,
                                                                                  final ConfiguredAirbyteCatalog catalog) {

    return catalog.getStreams().stream()
        .filter(s -> !initialLoadStreams.streamsForInitialLoad().contains(s))
        .filter(s -> s.getSyncMode() == SyncMode.INCREMENTAL)
        .map(s -> new AirbyteStreamNameNamespacePair(s.getStream().getName(), s.getStream().getNamespace()))
        .collect(Collectors.toSet());
  }

  @Override
  public AirbyteStateMessage createIntermediateStateMessage(final AirbyteStreamNameNamespacePair pair, final OrderedColumnLoadStatus ocLoadStatus) {
    final List<AirbyteStreamState> streamStates = streamsThatHaveCompletedSnapshot.stream()
        .map(s -> getAirbyteStreamState(s, Jsons.jsonNode(getFinalState(s))))
        .collect(Collectors.toList());

    streamStates.add(getAirbyteStreamState(pair, (Jsons.jsonNode(ocLoadStatus))));
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
  public AirbyteStateMessage createFinalStateMessage(final AirbyteStreamNameNamespacePair pair, final JsonNode streamStateForIncrementalRun) {
    streamsThatHaveCompletedSnapshot.add(pair);

    final List<AirbyteStreamState> streamStates = streamsThatHaveCompletedSnapshot.stream()
        .map(s -> getAirbyteStreamState(s, Jsons.jsonNode(getFinalState(s))))
        .collect(Collectors.toList());

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
