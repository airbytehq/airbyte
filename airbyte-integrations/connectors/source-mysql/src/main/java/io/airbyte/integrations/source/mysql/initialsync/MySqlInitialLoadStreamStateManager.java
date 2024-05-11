/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.InitialLoadStreams;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.PrimaryKeyInfo;
import io.airbyte.integrations.source.mysql.internal.models.PrimaryKeyLoadStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Map;
import java.util.Objects;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This state manager extends the StreamStateManager to enable writing the state_type and version
 * keys to the stream state when they're going through the iterator Once we have verified that
 * expanding StreamStateManager itself to include this functionality, this class will be removed
 */
public class MySqlInitialLoadStreamStateManager extends MySqlInitialLoadStateManager {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySqlInitialLoadStreamStateManager.class);

  public MySqlInitialLoadStreamStateManager(final ConfiguredAirbyteCatalog catalog,
                                            final InitialLoadStreams initialLoadStreams,
                                            final Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, PrimaryKeyInfo> pairToPrimaryKeyInfo) {
    this.pairToPrimaryKeyInfo = pairToPrimaryKeyInfo;
    this.pairToPrimaryKeyLoadStatus = MySqlInitialLoadStateManager.initPairToPrimaryKeyLoadStatusMap(initialLoadStreams.pairToInitialLoadStatus());
    this.streamStateForIncrementalRunSupplier = pair -> Jsons.emptyObject();
  }

  @Override
  public AirbyteStateMessage createFinalStateMessage(final ConfiguredAirbyteStream stream) {
    AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    final JsonNode incrementalState = getIncrementalState(pair);
    if (incrementalState == null || incrementalState.isEmpty()) {
      // resumeable full refresh
      return generateStateMessageAtCheckpoint(stream);
    }

    return new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(getAirbyteStreamState(pair, incrementalState));
  }

  @Override
  public PrimaryKeyInfo getPrimaryKeyInfo(final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair pair) {
    return pairToPrimaryKeyInfo.get(pair);
  }

  @Override
  public PrimaryKeyLoadStatus getPrimaryKeyLoadStatus(final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair pair) {
    return pairToPrimaryKeyLoadStatus.get(pair);
  }

  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint(final ConfiguredAirbyteStream stream) {
    AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    var pkStatus = getPrimaryKeyLoadStatus(pair);
    return new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(getAirbyteStreamState(pair, Jsons.jsonNode(pkStatus)));
  }

  protected AirbyteStreamState getAirbyteStreamState(final io.airbyte.protocol.models.AirbyteStreamNameNamespacePair pair, final JsonNode stateData) {
    LOGGER.info("STATE DATA FOR {}: {}", pair.getNamespace().concat("_").concat(pair.getName()), stateData);
    assert Objects.nonNull(pair.getName());
    assert Objects.nonNull(pair.getNamespace());

    return new AirbyteStreamState()
        .withStreamDescriptor(
            new StreamDescriptor().withName(pair.getName()).withNamespace(pair.getNamespace()))
        .withStreamState(stateData);
  }

}
