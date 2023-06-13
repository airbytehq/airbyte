package io.airbyte.integrations.source.postgres.ctid;

import static io.airbyte.integrations.source.postgres.ctid.CtidStateManager.CTID_STATUS_VERSION;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.AbstractIterator;
import io.airbyte.integrations.source.postgres.internal.models.CtidStatus;
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.util.Iterator;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.BiFunction;
import javax.annotation.CheckForNull;
import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class CtidStateIterator extends AbstractIterator<AirbyteMessage> implements Iterator<AirbyteMessage>
{
  private static final Logger LOGGER = LoggerFactory.getLogger(CtidStateIterator.class);
  private final Iterator<AirbyteMessage> messageIterator;
  private final AirbyteStreamNameNamespacePair pair;
  private boolean hasEmittedFinalState;
  private boolean hasCaughtException = false;
  private String lastCtid;
  private final JsonNode streamStateForIncrementalRun;
  final BiFunction<AirbyteStreamNameNamespacePair, JsonNode, AirbyteStateMessage> finalStateMessageSupplier;
  final AtomicLong recordCount = new AtomicLong();

  public CtidStateIterator(final Iterator<AirbyteMessage> messageIterator,
      final AirbyteStreamNameNamespacePair pair,
      final JsonNode streamStateForIncrementalRun,
      final BiFunction<AirbyteStreamNameNamespacePair, JsonNode, AirbyteStateMessage> finalStateMessageSupplier) {
    this.messageIterator = messageIterator;
    this.pair = pair;
    this.streamStateForIncrementalRun = streamStateForIncrementalRun;
    this.finalStateMessageSupplier = finalStateMessageSupplier;
  }

  @CheckForNull
  @Override
  protected AirbyteMessage computeNext() {
    final long count = recordCount.incrementAndGet();
    if (hasCaughtException) {
      // Mark iterator as done since the next call to messageIterator will result in an
      // IllegalArgumentException and resets exception caught state.
      // This occurs when the previous iteration emitted state so this iteration cycle will indicate
      // iteration is complete
      hasCaughtException = false;
      return endOfData();
    }

    if (messageIterator.hasNext()) {
      if (count % 1_000_000 == 0 && StringUtils.isNotBlank(lastCtid)) {
        LOGGER.info("saving ctid state with {}", this.lastCtid);
        return CtidStateManager.createStateMessage(pair,
            new CtidStatus()
                .withVer(CTID_STATUS_VERSION)
                .withType(CtidStatus.Type.CTID)
                .withCtid(lastCtid)
                .withIncrementalState(streamStateForIncrementalRun));
      }
      // Use try-catch to catch Exception that could occur when connection to the database fails
      try {
        final AirbyteMessage message = messageIterator.next();
        if (message.getRecord().getData().hasNonNull("ctid")) {
          this.lastCtid = message.getRecord().getData().get("ctid").asText();
        }
        return message;
      } catch (final Exception e) {
        hasCaughtException = true;
        LOGGER.error("Message iterator failed to read next record.", e);
        // We want to still continue attempting to sync future streams, so the exception is caught. When
        // frequent state emission is introduced, this
        // will result in a partial success.
        return endOfData();
      }
    } else if (!hasEmittedFinalState) {
      hasEmittedFinalState = true;
      return new AirbyteMessage()
          .withType(Type.STATE)
          .withState(finalStateMessageSupplier.apply(pair, streamStateForIncrementalRun));
    } else {
      return endOfData();
    }
  }
}
