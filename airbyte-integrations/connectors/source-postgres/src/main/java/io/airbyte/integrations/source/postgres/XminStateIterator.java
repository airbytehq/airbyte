package io.airbyte.integrations.source.postgres;

import autovalue.shaded.com.google.common.collect.AbstractIterator;
import io.airbyte.integrations.source.relationaldb.state.StateManager;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.Iterator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class XminStateIterator extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(XminStateIterator.class);

  private final Iterator<io.airbyte.protocol.models.v0.AirbyteMessage> messageIterator;
  private final StateManager stateManager;
  private final AirbyteStreamNameNamespacePair pair;
  private String currentMaxCursor;
  private boolean hasEmittedFinalState;

  private boolean hasCaughtException = false;


  /**
   * @param stateManager Manager that maintains connector state
   * @param pair Stream Name and Namespace (e.g. public.users)
   */
  public XminStateIterator(final Iterator<io.airbyte.protocol.models.v0.AirbyteMessage> messageIterator,
      final StateManager stateManager,
      final AirbyteStreamNameNamespacePair pair) {
    this.messageIterator = messageIterator;
    this.stateManager = stateManager;
    this.pair = pair;
  }

  /**
   * Computes the next record retrieved from Source stream. Emits StateMessage containing data of the
   * record that has been read so far
   *
   * <p>
   * If this method throws an exception, it will propagate outward to the {@code hasNext} or
   * {@code next} invocation that invoked this method. Any further attempts to use the iterator will
   * result in an {@link IllegalStateException}.
   * </p>
   *
   * @return {@link AirbyteStateMessage} containing information of the records read so far
   */
  @Override
  protected AirbyteMessage computeNext() {
    if (hasCaughtException) {
      // Mark iterator as done since the next call to messageIterator will result in an
      // IllegalArgumentException and resets exception caught state.
      // This occurs when the previous iteration emitted state so this iteration cycle will indicate
      // iteration is complete
      hasCaughtException = false;
      return endOfData();
    }

    if (messageIterator.hasNext()) {
      // Use try-catch to catch Exception that could occur when connection to the database fails
      try {
        final AirbyteMessage message = messageIterator.next();
        return message;
      } catch (final Exception e) {
        hasCaughtException = true;
        LOGGER.error("Message iterator failed to read next record.", e);
        return createStateMessage(false);
      }
    } else if (!hasEmittedFinalState) {
      return createStateMessage(true);
    } else {
      return endOfData();
    }
  }

  /**
   * Creates AirbyteStateMessage while updating the cursor used to checkpoint the state of records
   * read up so far
   *
   * @param isFinalState marker for if the final state of the iterator has been reached
   * @return AirbyteMessage which includes information on state of records read so far
   */
  public io.airbyte.protocol.models.v0.AirbyteMessage createStateMessage(final boolean isFinalState) {
    final StreamDescriptor streamDescriptor = new StreamDescriptor();
    streamDescriptor.setName(pair.getName());
    streamDescriptor.setNamespace(pair.getNamespace());
    final io.airbyte.protocol.models.v0.AirbyteStreamState streamState =
        new io.airbyte.protocol.models.v0.AirbyteStreamState();

    // Set state

    streamState.setStreamDescriptor(streamDescriptor);
    final AirbyteStateMessage stateMessage =
        new AirbyteStateMessage()
            .withType(AirbyteStateType.STREAM)
            .withStream(streamState);

    // final AirbyteStateMessage stateMessage = stateManager.emit(Optional.of(pair));
    if (isFinalState) {
      hasEmittedFinalState = true;
    }

    return new AirbyteMessage().withType(Type.STATE).withState(stateMessage);
  }
}
