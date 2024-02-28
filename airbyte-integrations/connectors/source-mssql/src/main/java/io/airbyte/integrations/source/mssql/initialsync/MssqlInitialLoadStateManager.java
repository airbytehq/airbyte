/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.relationaldb.models.InternalModels.StateType;
import io.airbyte.cdk.integrations.source.relationaldb.models.OrderedColumnLoadStatus;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIteratorManager;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil.OrderedColumnInfo;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Objects;
import java.util.function.Function;
import java.util.stream.Collectors;

public abstract class MssqlInitialLoadStateManager implements SourceStateIteratorManager<AirbyteMessage> {

  public static long MSSQL_STATE_VERSION = 2;
  public static String STATE_TYPE_KEY = "state_type";
  public static String ORDERED_COL_STATE_TYPE = "ordered_column";

  private OrderedColumnLoadStatus ocStatus;

  private Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier;

  private long syncCheckpointRecords;
  private Duration syncCheckpointDuration;

  /**
   * Returns an intermediate state message for the initial sync.
   *
   * @param pair pair
   * @param ocLoadStatus ordered column load status
   * @return state message
   */
  public abstract AirbyteStateMessage createIntermediateStateMessage(final AirbyteStreamNameNamespacePair pair, final OrderedColumnLoadStatus ocLoadStatus);

  /**
   * Updates the {@link OrderedColumnLoadStatus} for the state associated with the given pair.
   *
   * @param pair pair
   * @param ocLoadStatus updated status
   */
  public abstract void updateOrderedColumnLoadState(final AirbyteStreamNameNamespacePair pair, final OrderedColumnLoadStatus ocLoadStatus);

  /**
   * Returns the final state message for the initial sync..
   *
   * @param pair pair
   * @param streamStateForIncrementalRun incremental status
   * @return state message
   */
  public abstract AirbyteStateMessage createFinalStateMessage(final AirbyteStreamNameNamespacePair pair, final JsonNode streamStateForIncrementalRun);

  /**
   * Returns the previous state emitted. Represented as a {@link OrderedColumnLoadStatus} associated
   * with the stream.
   *
   * @param pair pair
   * @return load status
   */
  public abstract OrderedColumnLoadStatus getOrderedColumnLoadStatus(final AirbyteStreamNameNamespacePair pair);

  /**
   * Returns the current {@OrderedColumnInfo}, associated with the stream. This includes the data type
   * and the column name associated with the stream.
   *
   * @param pair pair
   * @return load status
   */
  public abstract OrderedColumnInfo getOrderedColumnInfo(final AirbyteStreamNameNamespacePair pair);

  static Map<AirbyteStreamNameNamespacePair, OrderedColumnLoadStatus> initPairToOrderedColumnLoadStatusMap(
                                                                                                           final Map<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair, OrderedColumnLoadStatus> pairToOcStatus) {
    return pairToOcStatus.entrySet().stream()
        .collect(Collectors.toMap(
            e -> new AirbyteStreamNameNamespacePair(e.getKey().getName(), e.getKey().getNamespace()),
            Entry::getValue));
  }


  @Override
  public AirbyteStateMessage generateStateMessageAtCheckpoint(final ConfiguredAirbyteStream stream) {
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    return createIntermediateStateMessage(pair, ocStatus);
  }

  @Override
  public AirbyteMessage processRecordMessage(final ConfiguredAirbyteStream stream, final AirbyteMessage message) {
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    final String ocFieldName = getOrderedColumnInfo(pair).ocFieldName();
    final String lastOcVal = message.getRecord().getData().get(ocFieldName).asText();
    ocStatus = new OrderedColumnLoadStatus()
        .withVersion(MSSQL_STATE_VERSION)
        .withStateType(StateType.ORDERED_COLUMN)
        .withOrderedCol(ocFieldName)
        .withOrderedColVal(lastOcVal)
        .withIncrementalState(getIncrementalState(stream));
    updateOrderedColumnLoadState(pair, ocStatus);
    return message;
  }

  @Override
  public AirbyteStateMessage createFinalStateMessage(final ConfiguredAirbyteStream stream) {
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    ocStatus = null;
    return createFinalStateMessage(pair, getIncrementalState(stream));
  }

  @Override
  public boolean shouldEmitStateMessage(final long recordCount, final Instant lastCheckpoint) {
    return (recordCount >= syncCheckpointRecords || Duration.between(lastCheckpoint, OffsetDateTime.now()).compareTo(syncCheckpointDuration) > 0)
        && Objects.nonNull(ocStatus);
  }

  public void setStreamStateForIncrementalRunSupplier(Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier) {
    this.streamStateForIncrementalRunSupplier = streamStateForIncrementalRunSupplier;
  }

  public void setCheckpointFrequency(final long syncCheckpointRecords, final Duration syncCheckpointDuration) {
    this.syncCheckpointDuration = syncCheckpointDuration;
    this.syncCheckpointRecords = syncCheckpointRecords;
  }

  private JsonNode getIncrementalState(final ConfiguredAirbyteStream stream) {
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    final OrderedColumnLoadStatus currentOcLoadStatus = getOrderedColumnLoadStatus(pair);

    return
        (currentOcLoadStatus == null || currentOcLoadStatus.getIncrementalState() == null)
            ? streamStateForIncrementalRunSupplier.apply(pair)
            : currentOcLoadStatus.getIncrementalState();
  }
}
