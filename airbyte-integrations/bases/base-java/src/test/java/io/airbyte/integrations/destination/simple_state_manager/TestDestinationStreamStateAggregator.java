package io.airbyte.integrations.destination.simple_state_manager;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.StreamDescriptor;
import java.util.LinkedHashSet;
import java.util.function.Supplier;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class TestDestinationStreamStateAggregator {

  @Test
  public void testProperEmissionOrder() {
    final Supplier<Long> mMsSupplier = Mockito.mock(Supplier.class);
    Mockito.when(mMsSupplier.get())
        .thenReturn(1L, 3L, 2L);

    final AirbyteStateMessage airbyteStateMessage1 = getStreamStateMessage("one");
    final AirbyteStateMessage airbyteStateMessageLate = getStreamStateMessage("late");
    final AirbyteStateMessage airbyteStateMessageEarly = getStreamStateMessage("early");

    final DestinationStateAggregator destinationStateAggregator = new DestinationStreamStateAggregator(mMsSupplier);

    destinationStateAggregator.ingest(airbyteStateMessage1);
    destinationStateAggregator.ingest(airbyteStateMessageLate);
    destinationStateAggregator.ingest(airbyteStateMessageEarly);

    final LinkedHashSet result = destinationStateAggregator.getStateMessages();

    Assertions.assertThat(result)
        .containsExactly(toMessage(airbyteStateMessage1), toMessage(airbyteStateMessageEarly), toMessage(airbyteStateMessageLate));
  }

  @Test
  public void testNoOverrideSameMilli() {
    final Supplier<Long> mMsSupplier = Mockito.mock(Supplier.class);
    Mockito.when(mMsSupplier.get())
        .thenReturn(1L, 1L, 1L);

    final AirbyteStateMessage airbyteStateMessage1 = getStreamStateMessage("one");
    final AirbyteStateMessage airbyteStateMessage2 = getStreamStateMessage("late");
    final AirbyteStateMessage airbyteStateMessage3 = getStreamStateMessage("early");

    final DestinationStateAggregator destinationStateAggregator = new DestinationStreamStateAggregator(mMsSupplier);

    destinationStateAggregator.ingest(airbyteStateMessage1);
    destinationStateAggregator.ingest(airbyteStateMessage2);
    destinationStateAggregator.ingest(airbyteStateMessage3);

    final LinkedHashSet result = destinationStateAggregator.getStateMessages();

    Assertions.assertThat(result)
        .containsExactlyInAnyOrder(toMessage(airbyteStateMessage1), toMessage(airbyteStateMessage3), toMessage(airbyteStateMessage2));
  }

  @Test
  public void testOverrideSameSd() {
    final Supplier<Long> mMsSupplier = Mockito.mock(Supplier.class);
    Mockito.when(mMsSupplier.get())
        .thenReturn(1L, 1L, 1L);

    final AirbyteStateMessage airbyteStateMessage1 = getStreamStateMessage("one", "one");
    final AirbyteStateMessage airbyteStateMessage2 = getStreamStateMessage("one", "two");
    final AirbyteStateMessage airbyteStateMessage3 = getStreamStateMessage("one", "three");

    final DestinationStateAggregator destinationStateAggregator = new DestinationStreamStateAggregator(mMsSupplier);

    destinationStateAggregator.ingest(airbyteStateMessage1);
    destinationStateAggregator.ingest(airbyteStateMessage2);
    destinationStateAggregator.ingest(airbyteStateMessage3);

    final LinkedHashSet result = destinationStateAggregator.getStateMessages();

    Assertions.assertThat(result)
        .containsOnly(toMessage(airbyteStateMessage3));
  }

  private AirbyteStateMessage getStreamStateMessage(final String name) {
    return new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState()
                .withStreamDescriptor(
                    new StreamDescriptor()
                        .withName(name)
                )
        );
  }

  private AirbyteStateMessage getStreamStateMessage(final String name, final String state) {
    return new AirbyteStateMessage()
        .withType(AirbyteStateType.STREAM)
        .withStream(
            new AirbyteStreamState()
                .withStreamDescriptor(
                    new StreamDescriptor()
                        .withName(name)
                )
                .withStreamState(Jsons.jsonNode(state))
        );
  }

  private AirbyteMessage toMessage(final AirbyteStateMessage airbyteStateMessage) {
    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(airbyteStateMessage);
  }
}
