/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres;

import autovalue.shaded.com.google.common.collect.AbstractIterator;
import io.airbyte.integrations.source.jdbc.iblt.InvertibleBloomFilter;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.util.Iterator;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MagicSyncStateIterator extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MagicSyncStateIterator.class);

  private final Iterator<io.airbyte.protocol.models.v0.AirbyteMessage> messageIterator;
  private final AirbyteStreamNameNamespacePair pair;
  private boolean hasEmittedFinalState;

  private boolean hasCaughtException = false;
  private final InvertibleBloomFilter prevStateBloomFilter;
  private final InvertibleBloomFilter currStateBloomFilter;

  /**
   * @param pair Stream Name and Namespace (e.g. public.users)
   */
  public MagicSyncStateIterator(final Iterator<io.airbyte.protocol.models.v0.AirbyteMessage> messageIterator,
      final AirbyteStreamNameNamespacePair pair,
      final InvertibleBloomFilter prevStateBloomFilter) {
    this.messageIterator = messageIterator;
    this.pair = pair;
    this.prevStateBloomFilter = prevStateBloomFilter;
    this.currStateBloomFilter = new InvertibleBloomFilter();
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
        AirbyteMessage message = messageIterator.next();
        while(inPrevState(message)) {
          currStateBloomFilter.insert(
              message.getRecord().getData().get("key_hash").asText(),
              message.getRecord().getData().get("val_hash").asText());

          if (messageIterator.hasNext()) {
            message = messageIterator.next();
          } else {
            // Emit the state.
            hasEmittedFinalState = true;
            LOGGER.info("Attempting to emit the state");
            return MagicSyncStateManager.createStateMessage(pair, currStateBloomFilter);
          }
        }

        // Add the current message to the bloom filter
        currStateBloomFilter.insert(
            message.getRecord().getData().get("key_hash").asText(),
            message.getRecord().getData().get("val_hash").asText());
        return message;
      } catch (final Exception e) {
        hasCaughtException = true;
        LOGGER.error("Message iterator failed to read next record.", e);
        return endOfData();
      }
    } else if (!hasEmittedFinalState) {
      hasEmittedFinalState = true;
      LOGGER.info("Attempting to emit the state");
      return MagicSyncStateManager.createStateMessage(pair, currStateBloomFilter);
    } else {
      return endOfData();
    }
  }

  private boolean inPrevState(final AirbyteMessage message) {
    if (prevStateBloomFilter == null) {
      return false;
    }
    final String keyHash = message.getRecord().getData().get("key_hash").asText();
    final String valHash = message.getRecord().getData().get("key_hash").asText();
    return prevStateBloomFilter.contains(keyHash) && prevStateBloomFilter.getValue(keyHash).equals(valHash);
  }
}
