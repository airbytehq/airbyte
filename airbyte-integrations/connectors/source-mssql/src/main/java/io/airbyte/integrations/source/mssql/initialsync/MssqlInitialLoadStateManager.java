/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.initialsync;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.relationaldb.models.OrderedColumnLoadStatus;
import io.airbyte.integrations.source.mssql.initialsync.MssqlInitialReadUtil.OrderedColumnInfo;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.util.Map;
import java.util.Map.Entry;
import java.util.stream.Collectors;

public interface MssqlInitialLoadStateManager {

  public static long MSSQL_STATE_VERSION = 2;
  String STATE_TYPE_KEY = "state_type";
  String ORDERED_COL_STATE_TYPE = "ordered_column";

  /**
   * Returns an intermediate state message for the initial sync.
   *
   * @param pair pair
   * @param ocLoadStatus ordered column load status
   * @return state message
   */
  AirbyteStateMessage createIntermediateStateMessage(final AirbyteStreamNameNamespacePair pair, final OrderedColumnLoadStatus ocLoadStatus);

  /**
   * Updates the {@link OrderedColumnLoadStatus} for the state associated with the given pair.
   *
   * @param pair pair
   * @param ocLoadStatus updated status
   */
  void updateOrderedColumnLoadState(final AirbyteStreamNameNamespacePair pair, final OrderedColumnLoadStatus ocLoadStatus);

  /**
   * Returns the final state message for the initial sync..
   *
   * @param pair pair
   * @param streamStateForIncrementalRun incremental status
   * @return state message
   */
  AirbyteStateMessage createFinalStateMessage(final AirbyteStreamNameNamespacePair pair, final JsonNode streamStateForIncrementalRun);

  /**
   * Returns the previous state emitted. Represented as a {@link OrderedColumnLoadStatus} associated
   * with the stream.
   *
   * @param pair pair
   * @return load status
   */
  OrderedColumnLoadStatus getOrderedColumnLoadStatus(final AirbyteStreamNameNamespacePair pair);

  /**
   * Returns the current {@OrderedColumnInfo}, associated with the stream. This includes the data type
   * and the column name associated with the stream.
   *
   * @param pair pair
   * @return load status
   */
  OrderedColumnInfo getOrderedColumnInfo(final AirbyteStreamNameNamespacePair pair);

  static Map<AirbyteStreamNameNamespacePair, OrderedColumnLoadStatus> initPairToOrderedColumnLoadStatusMap(
                                                                                                           final Map<io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair, OrderedColumnLoadStatus> pairToOcStatus) {
    return pairToOcStatus.entrySet().stream()
        .collect(Collectors.toMap(
            e -> new AirbyteStreamNameNamespacePair(e.getKey().getName(), e.getKey().getNamespace()),
            Entry::getValue));
  }

}
