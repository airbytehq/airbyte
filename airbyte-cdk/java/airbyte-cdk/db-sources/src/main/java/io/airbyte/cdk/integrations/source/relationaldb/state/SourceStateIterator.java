/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.source.relationaldb.state;

import com.google.common.collect.AbstractIterator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateStats;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.time.Duration;
import java.time.Instant;
import java.time.OffsetDateTime;
import java.util.Iterator;
import javax.annotation.CheckForNull;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class SourceStateIterator<T> extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(SourceStateIterator.class);
  private final Iterator<T> messageIterator;
  private final ConfiguredAirbyteStream stream;
  private final StateEmitFrequency stateEmitFrequency;
  private boolean hasEmittedFinalState = false;
  private long recordCount = 0L;
  private Instant lastCheckpoint = Instant.now();

  private final SourceStateMessageProducer sourceStateMessageProducer;

  public SourceStateIterator(final Iterator<T> messageIterator,
                             final ConfiguredAirbyteStream stream,
                             final SourceStateMessageProducer sourceStateMessageProducer,
                             final StateEmitFrequency stateEmitFrequency) {
    this.messageIterator = messageIterator;
    this.stream = stream;
    this.sourceStateMessageProducer = sourceStateMessageProducer;
    this.stateEmitFrequency = stateEmitFrequency;
  }

  @CheckForNull
  @Override
  protected AirbyteMessage computeNext() {

    boolean iteratorHasNextValue = false;
    try {
      iteratorHasNextValue = messageIterator.hasNext();
    } catch (final Exception ex) {
      // If the initial snapshot is incomplete for this stream, throw an exception failing the sync. This
      // will ensure the platform retry logic
      // kicks in and keeps retrying the sync until the initial snapshot is complete.
      throw new RuntimeException(ex);
    }
    if (iteratorHasNextValue) {
      if (shouldEmitStateMessage() && sourceStateMessageProducer.shouldEmitStateMessage(stream)) {
        final AirbyteStateMessage stateMessage = sourceStateMessageProducer.generateStateMessageAtCheckpoint(stream);
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
        final AirbyteMessage processedMessage = sourceStateMessageProducer.processRecordMessage(stream, message);
        recordCount++;
        return processedMessage;
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    } else if (!hasEmittedFinalState) {
      hasEmittedFinalState = true;
      final AirbyteStateMessage finalStateMessageForStream = sourceStateMessageProducer.createFinalStateMessage(stream);
      finalStateMessageForStream.withSourceStats(new AirbyteStateStats().withRecordCount((double) recordCount));
      recordCount = 0L;
      return new AirbyteMessage()
          .withType(Type.STATE)
          .withState(finalStateMessageForStream);
    } else {
      return endOfData();
    }
  }

  private boolean shouldEmitStateMessage() {
    return (recordCount >= stateEmitFrequency.syncCheckpointRecords()
        || Duration.between(lastCheckpoint, OffsetDateTime.now()).compareTo(stateEmitFrequency.syncCheckpointDuration()) > 0);

  }

}
