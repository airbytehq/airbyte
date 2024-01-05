/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.relationaldb.state;

import com.google.common.collect.AbstractIterator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateStats;
import java.time.Instant;
import java.util.Iterator;
import javax.annotation.CheckForNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SourceStateIterator<T> extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SourceStateIterator.class);
  private final Iterator<T> messageIterator;
  private boolean hasEmittedFinalState = false;
  private long recordCount = 0L;
  private Instant lastCheckpoint = Instant.now();

  private final SourceStateIteratorManager sourceStateIteratorManager;

  public SourceStateIterator(final Iterator<T> messageIterator,
                             final SourceStateIteratorManager sourceStateIteratorManager) {
    this.messageIterator = messageIterator;
    this.sourceStateIteratorManager = sourceStateIteratorManager;
  }

  @CheckForNull
  @Override
  protected AirbyteMessage computeNext() {
    boolean iteratorHasNextValue = false;
    try {
      iteratorHasNextValue = messageIterator.hasNext();
    } catch (Exception ex) {
      LOGGER.info("Caught exception while trying to get the next from message iterator. Treating hasNext to false. ", ex);
    }
    if (iteratorHasNextValue) {
      if (sourceStateIteratorManager.shouldEmitStateMessage(recordCount, lastCheckpoint)) {
        AirbyteStateMessage stateMessage = sourceStateIteratorManager.generateStateMessageAtCheckpoint();
        stateMessage.withSourceStats(new AirbyteStateStats().withRecordCount((double) recordCount));

        recordCount = 0L;
        lastCheckpoint = Instant.now();
        return new AirbyteMessage()
            .withType(Type.STATE)
            .withState(stateMessage);
      }
      // Use try-catch to catch Exception that could occur when connection to the database fails
      try {
        final T message = messageIterator.next();
        final AirbyteMessage processedMessage = sourceStateIteratorManager.processRecordMessage(message);
        recordCount++;
        return processedMessage;
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    } else if (!hasEmittedFinalState) {
      hasEmittedFinalState = true;
      final AirbyteStateMessage finalStateMessage = sourceStateIteratorManager.createFinalStateMessage();
      return new AirbyteMessage()
          .withType(Type.STATE)
          .withState(finalStateMessage);
    } else {
      return endOfData();
    }
  }

}
