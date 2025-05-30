/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.relationaldb.models.InternalModels.StateType;
import io.airbyte.cdk.integrations.source.relationaldb.models.OrderedColumnLoadStatus;
import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateMessageProducer;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil.OrderedColumnInfo;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Objects;
import java.util.function.Function;
import java.util.stream.Collectors;

public abstract class MssqlInitialLoadStateManager implements SourceStateMessageProducer<AirbyteMessage> {

  public static final long MSSQL_STATE_VERSION = 2;
  public static final String STATE_TYPE_KEY = "state_type";
  public static final String ORDERED_COL_STATE_TYPE = "ordered_column";
  protected Map<AirbyteStreamNameNamespacePair, OrderedColumnLoadStatus> pairToOrderedColLoadStatus;
  protected Map<AirbyteStreamNameNamespacePair, OrderedColumnInfo> pairToOrderedColInfo;

  private OrderedColumnLoadStatus ocStatus;

  protected Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier;

  void setStreamStateForIncrementalRunSupplier(final Function<AirbyteStreamNameNamespacePair, JsonNode> streamStateForIncrementalRunSupplier) {
    this.streamStateForIncrementalRunSupplier = streamStateForIncrementalRunSupplier;
  }

  /**
   * Updates the {@link OrderedColumnLoadStatus} for the state associated with the given pair.
   *
   * @param pair pair
   * @param ocLoadStatus updated status
   */
  public void updateOrderedColumnLoadState(final AirbyteStreamNameNamespacePair pair, final OrderedColumnLoadStatus ocLoadStatus) {
    pairToOrderedColLoadStatus.put(pair, ocLoadStatus);
  }

  /**
   * Returns the previous state emitted. Represented as a {@link OrderedColumnLoadStatus} associated
   * with the stream.
   *
   * @param pair pair
   * @return load status
   */
  public OrderedColumnLoadStatus getOrderedColumnLoadStatus(final AirbyteStreamNameNamespacePair pair) {
    return pairToOrderedColLoadStatus.get(pair);
  }

  /**
   * Returns the current {@OrderedColumnInfo}, associated with the stream. This includes the data type
   * and the column name associated with the stream.
   *
   * @param pair pair
   * @return load status
   */
  public OrderedColumnInfo getOrderedColumnInfo(final AirbyteStreamNameNamespacePair pair) {
    return pairToOrderedColInfo.get(pair);
  }

  static Map<AirbyteStreamNameNamespacePair, OrderedColumnLoadStatus> initPairToOrderedColumnLoadStatusMap(
                                                                                                           final Map<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair, OrderedColumnLoadStatus> pairToOcStatus) {
    return pairToOcStatus.entrySet().stream()
        .collect(Collectors.toMap(
            e -> new AirbyteStreamNameNamespacePair(e.getKey().getName(), e.getKey().getNamespace()),
            Entry::getValue));
  }

  protected JsonNode getIncrementalState(final AirbyteStreamNameNamespacePair pair) {
    final OrderedColumnLoadStatus currentOcLoadStatus = getOrderedColumnLoadStatus(pair);
    return (currentOcLoadStatus == null || currentOcLoadStatus.getIncrementalState() == null) ? streamStateForIncrementalRunSupplier.apply(pair)
        : currentOcLoadStatus.getIncrementalState();
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
  public boolean shouldEmitStateMessage(final ConfiguredAirbyteStream stream) {
    return Objects.nonNull(getOrderedColumnInfo(new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace())));
  }

  private JsonNode getIncrementalState(final ConfiguredAirbyteStream stream) {
    final AirbyteStreamNameNamespacePair pair = new AirbyteStreamNameNamespacePair(stream.getStream().getName(), stream.getStream().getNamespace());
    final OrderedColumnLoadStatus currentOcLoadStatus = getOrderedColumnLoadStatus(pair);

    return (currentOcLoadStatus == null || currentOcLoadStatus.getIncrementalState() == null)
        ? streamStateForIncrementalRunSupplier.apply(pair)
        : currentOcLoadStatus.getIncrementalState();
  }

}
