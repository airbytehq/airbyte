/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.xmin;

import autovalue.shaded.com.google.common.collect.AbstractIterator;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.util.Iterator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class XminStateIterator extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(XminStateIterator.class);

  private final Iterator<io.airbyte.protocol.models.v0.AirbyteMessage> messageIterator;
  private final AirbyteStreamNameNamespacePair pair;
  private boolean hasEmittedFinalState;

  private boolean hasCaughtException = false;
  private final XminStatus xminStatus;

  /**
   * @param pair Stream Name and Namespace (e.g. public.users)
   */
  public XminStateIterator(final Iterator<io.airbyte.protocol.models.v0.AirbyteMessage> messageIterator,
                           final AirbyteStreamNameNamespacePair pair,
                           final XminStatus xminStatus) {
    this.messageIterator = messageIterator;
    this.pair = pair;
    this.xminStatus = xminStatus;
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
        // When intermediate state is supported, this should be modified to return endofData() and not fail the sync.
        throw e;
      }
    } else if (!hasEmittedFinalState) {
      hasEmittedFinalState = true;
      return XminStateManager.createStateMessage(pair, xminStatus);
    } else {
      return endOfData();
    }
  }
}
