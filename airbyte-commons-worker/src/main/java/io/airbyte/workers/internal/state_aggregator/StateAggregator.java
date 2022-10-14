/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal.state_aggregator;

import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteStateMessage;

public interface StateAggregator {

  void ingest(AirbyteStateMessage stateMessage);

  State getAggregated();

}
