/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import io.airbyte.protocol.models.AirbyteMessage;
import java.util.Queue;

public interface DestinationStateManager {

  void addState(AirbyteMessage message);

  Queue<AirbyteMessage> listAllPendingState();

  void markAllReceivedMessagesAsFlushedToTmpDestination();

  Queue<AirbyteMessage> listAllFlushedButNotCommittedState();

  void markAllFlushedMessageAsCommitted();

  Queue<AirbyteMessage> listAllCommittedState();

}
