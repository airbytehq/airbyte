package io.airbyte.integrations.destination.simple_state_manager;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.AbstractCollection;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashSet;
import java.util.Map;
import java.util.TreeSet;
import java.util.function.Supplier;
import lombok.Value;

public class DestinationStreamStateAggregator implements DestinationStateAggregator{

  @Value
  private class MessageWithEmitTime  {
    private long timestamp;
    private AirbyteStateMessage airbyteStateMessage;
  }

  private final Supplier<Long> currentMillisecondSupplier;

  private final Map<StreamDescriptor, MessageWithEmitTime> aggregatedState = new HashMap<>();

  public DestinationStreamStateAggregator() {
    this (() -> System.currentTimeMillis());
  }

  @VisibleForTesting
  DestinationStreamStateAggregator(final Supplier<Long> currentMillisecondSupplier) {
    this.currentMillisecondSupplier = currentMillisecondSupplier;
  }

  @Override public void ingest(final AirbyteStateMessage stateMessage) {
    aggregatedState.put(stateMessage.getStream().getStreamDescriptor(), new MessageWithEmitTime(currentMillisecondSupplier.get(), stateMessage));
  }

  @Override public LinkedHashSet<AirbyteMessage> getStateMessages() {
    final TreeSet<MessageWithEmitTime> sortedValues = new TreeSet<>(
        Comparator.comparingLong(MessageWithEmitTime::getTimestamp)
            .thenComparing(entry -> entry.getAirbyteStateMessage().getStream().getStreamDescriptor().getNamespace(),
                Comparator.nullsFirst(Comparator.naturalOrder()))
            .thenComparing(entry -> entry.getAirbyteStateMessage().getStream().getStreamDescriptor().getName())
    );

    aggregatedState.forEach((streamDescriptor, messageWithEmitTime) -> sortedValues.add(messageWithEmitTime));

    return sortedValues.stream().map(messageWithEmitTime -> new AirbyteMessage()
        .withType(Type.STATE)
        .withState(messageWithEmitTime.getAirbyteStateMessage())).collect(
        () -> new LinkedHashSet<>(),
        HashSet::add,
        AbstractCollection::addAll
    );
  }
}
