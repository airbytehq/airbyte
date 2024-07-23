/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.singlestore.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateMessageProducer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.singlestore.initialsync.SingleStoreInitialReadUtil.InitialLoadStreams;
import io.airbyte.integrations.source.singlestore.initialsync.SingleStoreInitialReadUtil.PrimaryKeyInfo;
import io.airbyte.integrations.source.singlestore.internal.models.InternalModels.StateType;
import io.airbyte.integrations.source.singlestore.internal.models.PrimaryKeyLoadStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamState;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SingleStoreInitialLoadStreamStateManager implements SourceStateMessageProducer<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SingleStoreInitialLoadStreamStateManager.class);
  public static final String STATE_TYPE_KEY = "state_type";
  public static final String PRIMARY_KEY_STATE_TYPE = "primary_key";
  private Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier;
  private final Map<AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> pairToPrimaryKeyLoadStatus;
  // Map of pair to the primary key info (field name & data type) associated with it.
  private final Map<AirbyteStreamNameNamespacePair, PrimaryKeyInfo> pairToPrimaryKeyInfo;

  public SingleStoreInitialLoadStreamStateManager(final InitialLoadStreams initialLoadStreams,
                                                  final Map<AirbyteStreamNameNamespacePair, PrimaryKeyInfo> pairToPrimaryKeyInfo) {
    this.pairToPrimaryKeyInfo = pairToPrimaryKeyInfo;
    this.pairToPrimaryKeyLoadStatus = initPairToPrimaryKeyLoadStatusMap(initialLoadStreams.pairToInitialLoadStatus());
  }

  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint(final ConfiguredAirbyteStream stream) {
    AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    var pkStatus = getPrimaryKeyLoadStatus(pair);
    return new AirbyteStateMessage().withType(AirbyteStateType.STREAM).withStream(getAirbyteStreamState(pair, Jsons.jsonNode(pkStatus)));
  }

  @Override
  public AirbyteMessage processRecordMessage(final ConfiguredAirbyteStream stream, final AirbyteMessage message) {
    if (Objects.nonNull(message)) {
      final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
      final String pkFieldName = this.getPrimaryKeyInfo(pair).pkFieldName();
      final String lastPk = message.getRecord().getData().get(pkFieldName).asText();
      final PrimaryKeyLoadStatus pkStatus = new PrimaryKeyLoadStatus().withStateType(StateType.PRIMARY_KEY).withPkName(pkFieldName).withPkVal(lastPk)
          .withIncrementalState(getIncrementalState(pair));
      pairToPrimaryKeyLoadStatus.put(pair, pkStatus);
    }
    return message;
  }

  @Override
  public AirbyteStateMessage createFinalStateMessage(final ConfiguredAirbyteStream stream) {
    AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    final JsonNode incrementalState = getIncrementalState(pair);
    return new AirbyteStateMessage().withType(AirbyteStateType.STREAM).withStream(getAirbyteStreamState(pair, incrementalState));
  }

  @Override
  public boolean shouldEmitStateMessage(final ConfiguredAirbyteStream stream) {
    return true;
  }

  void setStreamStateForIncrementalRunSupplier(final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier) {
    this.streamStateForIncrementalRunSupplier = streamStateForIncrementalRunSupplier;
  }

  public PrimaryKeyLoadStatus getPrimaryKeyLoadStatus(final AirbyteStreamNameNamespacePair pair) {
    return pairToPrimaryKeyLoadStatus.get(pair);
  }

  public PrimaryKeyInfo getPrimaryKeyInfo(final AirbyteStreamNameNamespacePair pair) {
    return pairToPrimaryKeyInfo.get(pair);
  }

  private JsonNode getIncrementalState(final AirbyteStreamNameNamespacePair pair) {
    final PrimaryKeyLoadStatus currentPkLoadStatus = getPrimaryKeyLoadStatus(pair);
    return (currentPkLoadStatus == null || currentPkLoadStatus.getIncrementalState() == null) ? streamStateForIncrementalRunSupplier.apply(pair)
        : currentPkLoadStatus.getIncrementalState();
  }

  private static AirbyteStreamState getAirbyteStreamState(final AirbyteStreamNameNamespacePair pair, final JsonNode stateData) {
    LOGGER.info("STATE DATA FOR {}: {}", pair.getNamespace().concat("_").concat(pair.getName()), stateData);
    assert Objects.nonNull(pair.getName());
    assert Objects.nonNull(pair.getNamespace());
    return new AirbyteStreamState().withStreamDescriptor(new StreamDescriptor().withName(pair.getName()).withNamespace(pair.getNamespace()))
        .withStreamState(stateData);
  }

  private static Map<AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> initPairToPrimaryKeyLoadStatusMap(
                                                                                                             final Map<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> pairToPkStatus) {
    final Map<AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> map = new HashMap<>();
    pairToPkStatus.forEach((pair, pkStatus) -> {
      final AirbyteStreamNameNamespacePair updatedPair = new AirbyteStreamNameNamespacePair(pair.getName(), pair.getNamespace());
      map.put(updatedPair, pkStatus);
    });
    return map;
  }

}
