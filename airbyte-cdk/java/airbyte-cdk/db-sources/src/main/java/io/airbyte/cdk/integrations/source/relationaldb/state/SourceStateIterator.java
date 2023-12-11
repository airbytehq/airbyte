package io.airbyte.cdk.integrations.source.relationaldb.state;

import com.google.common.collect.AbstractIterator;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateStats;
import java.time.Instant;
import java.util.Iterator;
import javax.annotation.CheckForNull;

public class SourceStateIterator extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage>  {
  private final Iterator<AirbyteMessage> messageIterator;
  private boolean hasEmittedFinalState = false;
  private long recordCount = 0L;
  private Instant lastCheckpoint = Instant.now();

  private final SourceStateIteratorProcessor sourceStateIteratorProcessor;

  public SourceStateIterator(final Iterator<AirbyteMessage> messageIterator,
      final SourceStateIteratorProcessor sourceStateIteratorProcessor) {
    this.messageIterator = messageIterator;
    this.sourceStateIteratorProcessor = sourceStateIteratorProcessor;
  }

  @CheckForNull
  @Override
  protected AirbyteMessage computeNext() {
    if (messageIterator.hasNext()) {
      if (sourceStateIteratorProcessor.shouldEmitStateMessage(recordCount, lastCheckpoint)) {
        AirbyteStateMessage stateMessage = sourceStateIteratorProcessor.generateStateMessageAtCheckpoint();
        stateMessage.withSourceStats(new AirbyteStateStats().withRecordCount((double) recordCount));

        recordCount = 0L;
        lastCheckpoint = Instant.now();
        return new AirbyteMessage()
            .withType(Type.STATE)
            .withState(stateMessage);
      }
      // Use try-catch to catch Exception that could occur when connection to the database fails
      try {
        final AirbyteMessage message = messageIterator.next();
        sourceStateIteratorProcessor.processRecordMessage(message);
        recordCount++;
        return message;
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    } else if (!hasEmittedFinalState) {
      hasEmittedFinalState = true;
      final AirbyteStateMessage finalStateMessage = sourceStateIteratorProcessor.createFinalStateMessage();
      return new AirbyteMessage()
          .withType(Type.STATE)
          .withState(finalStateMessage);
    } else {
      return endOfData();
    }
  }


}
