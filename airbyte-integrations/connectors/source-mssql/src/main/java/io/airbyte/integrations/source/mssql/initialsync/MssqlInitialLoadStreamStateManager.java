/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Preconditions;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil.InitialLoadStreams;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil.OrderedColumnInfo;
import io.airbyte.protocol.models.v0.*;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This state manager extends the StreamStateManager to enable writing the state_type and version
 * keys to the stream state when they're going through the iterator Once we have verified that
 * expanding StreamStateManager itself to include this functionality, this class will be removed
 */
public class MssqlInitialLoadStreamStateManager extends MssqlInitialLoadStateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(MssqlInitialLoadStateManager.class);
  private final Map<AirbyteStreamNameNamespacePair, OrderedColumnInfo> pairToOrderedColInfo;

  public MssqlInitialLoadStreamStateManager(final ConfiguredAirbyteCatalog catalog,
                                            final InitialLoadStreams initialLoadStreams,
                                            final Map<AirbyteStreamNameNamespacePair, OrderedColumnInfo> pairToOrderedColInfo) {
    this.pairToOrderedColInfo = pairToOrderedColInfo;
    this.pairToOrderedColLoadStatus = MssqlInitialLoadStateManager.initPairToOrderedColumnLoadStatusMap(initialLoadStreams.pairToInitialLoadStatus());
    this.streamStateForIncrementalRunSupplier = pair -> Jsons.emptyObject();
  }

  @Override
  public AirbyteStateMessage createFinalStateMessage(final ConfiguredAirbyteStream stream) {
    AirbyteStreamNameNamespacePair pair =
        new io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    final JsonNode incrementalState = getIncrementalState(pair);
    // If there is no incremental state, save the latest OC state
    // Such as in the case of full refresh
    final JsonNode finalState;
    if (incrementalState == null || incrementalState.isEmpty()) {
      finalState = Jsons.jsonNode(getOrderedColumnLoadStatus(pair));
    } else {
      finalState = incrementalState;
    }
    return new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(getAirbyteStreamState(pair, finalState));
  }

  @Override
  public OrderedColumnInfo getOrderedColumnInfo(final AirbyteStreamNameNamespacePair pair) {
    return pairToOrderedColInfo.get(pair);
  }

  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint(final ConfiguredAirbyteStream stream) {
    AirbyteStreamNameNamespacePair pair =
        new io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    var ocStatus = getOrderedColumnLoadStatus(pair);
    return new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(getAirbyteStreamState(pair, Jsons.jsonNode(ocStatus)));
  }

  protected AirbyteStreamState getAirbyteStreamState(final AirbyteStreamNameNamespacePair pair, final JsonNode stateData) {
    Preconditions.checkNotNull(pair);
    Preconditions.checkNotNull(pair.getName());
    Preconditions.checkNotNull(pair.getNamespace());
    LOGGER.info("State data for {}: {}", pair.getNamespace().concat("_").concat(pair.getName()), stateData);

    return new AirbyteStreamState()
        .withStreamDescriptor(
            new StreamDescriptor().withName(pair.getName()).withNamespace(pair.getNamespace()))
        .withStreamState(stateData);
  }

}
