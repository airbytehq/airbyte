/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateMessageProducer;
import io.airbyte.integrations.source.mysql.initialsync.MySqlInitialReadUtil.PrimaryKeyInfo;
import io.airbyte.integrations.source.mysql.internal.models.InternalModels.StateType;
import io.airbyte.integrations.source.mysql.internal.models.PrimaryKeyLoadStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.function.Function;

public abstract class MySqlInitialLoadStateManager implements SourceStateMessageProducer<AirbyteMessage> {

  public static final long MYSQL_STATUS_VERSION = 2;
  public static final String STATE_TYPE_KEY = "state_type";
  public static final String PRIMARY_KEY_STATE_TYPE = "primary_key";

  protected Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier;

  protected Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> pairToPrimaryKeyLoadStatus;

  // Map of pair to the primary key info (field name & data type) associated with it.
  protected Map<io.airbyte.protocol.models.AirbyteStreamNameNamespacePair, PrimaryKeyInfo> pairToPrimaryKeyInfo;

  void setStreamStateForIncrementalRunSupplier(final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier) {
    this.streamStateForIncrementalRunSupplier = streamStateForIncrementalRunSupplier;
  }

  // Updates the {@link PrimaryKeyLoadStatus} for the state associated with the given pair
  public void updatePrimaryKeyLoadState(final AirbyteStreamNameNamespacePair pair, final PrimaryKeyLoadStatus pkLoadStatus) {
    pairToPrimaryKeyLoadStatus.put(pair, pkLoadStatus);
  }

  // Returns the previous state emitted, represented as a {@link PrimaryKeyLoadStatus} associated with
  // the stream.
  public PrimaryKeyLoadStatus getPrimaryKeyLoadStatus(final AirbyteStreamNameNamespacePair pair) {
    return pairToPrimaryKeyLoadStatus.get(pair);
  }

  // Returns the current {@PrimaryKeyInfo}, associated with the stream. This includes the data type &
  // the column name associated with the stream.
  public abstract PrimaryKeyInfo getPrimaryKeyInfo(final AirbyteStreamNameNamespacePair pair);

  protected JsonNode getIncrementalState(final AirbyteStreamNameNamespacePair pair) {
    final PrimaryKeyLoadStatus currentPkLoadStatus = getPrimaryKeyLoadStatus(pair);
    return (currentPkLoadStatus == null || currentPkLoadStatus.getIncrementalState() == null) ? streamStateForIncrementalRunSupplier.apply(pair)
        : currentPkLoadStatus.getIncrementalState();
  }

  @Override
  public AirbyteMessage processRecordMessage(final ConfiguredAirbyteStream stream, final AirbyteMessage message) {
    if (Objects.nonNull(message)) {
      final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
      final String pkFieldName = this.getPrimaryKeyInfo(pair).pkFieldName();
      final String lastPk = message.getRecord().getData().get(pkFieldName).asText();
      final PrimaryKeyLoadStatus pkStatus = new PrimaryKeyLoadStatus()
          .withVersion(MYSQL_STATUS_VERSION)
          .withStateType(StateType.PRIMARY_KEY)
          .withPkName(pkFieldName)
          .withPkVal(lastPk)
          .withIncrementalState(getIncrementalState(pair));
      this.updatePrimaryKeyLoadState(pair, pkStatus);
    }
    return message;
  }

  @Override
  public boolean shouldEmitStateMessage(final ConfiguredAirbyteStream stream) {
    return true;
  }

  public static Map<AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> initPairToPrimaryKeyLoadStatusMap(
                                                                                                            final Map<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> pairToPkStatus) {
    final Map<AirbyteStreamNameNamespacePair, PrimaryKeyLoadStatus> map = new HashMap<>();
    pairToPkStatus.forEach((pair, pkStatus) -> {
      final AirbyteStreamNameNamespacePair updatedPair = new AirbyteStreamNameNamespacePair(pair.getName(), pair.getNamespace());
      map.put(updatedPair, pkStatus);
    });
    return map;
  }

}
