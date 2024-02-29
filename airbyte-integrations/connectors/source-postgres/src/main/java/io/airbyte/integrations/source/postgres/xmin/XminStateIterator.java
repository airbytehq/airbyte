/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.xmin;

import io.airbyte.cdk.integrations.source.relationaldb.state.SourceStateIterator;
import io.airbyte.cdk.integrations.source.relationaldb.state.StateEmitFrequency;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.time.Duration;
import java.util.Iterator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class XminStateIterator extends SourceStateIterator<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(XminStateIterator.class);

  private boolean hasCaughtException = false;

  public XminStateIterator(final Iterator<io.airbyte.protocol.models.v0.AirbyteMessage> messageIterator,
                           final ConfiguredAirbyteStream stream,
                           final XminStateManager manager) {
    // Emit frequency does not matter because we do not send state message for checkpointing in xmin
    // mode.
    // We only send state message at the end of the sync.
    super(messageIterator, stream, manager, new StateEmitFrequency(0L, Duration.ofSeconds(1L)));
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
    try {
      return super.computeNext();
    } catch (final RuntimeException ex) {
      hasCaughtException = true;
      LOGGER.error("Message iterator failed to read next record.", ex);
      // We want to still continue attempting to sync future streams, so the exception is caught. When
      // frequent state emission is introduced, this
      // will result in a partial success.
      return endOfData();
    }
  }

}
