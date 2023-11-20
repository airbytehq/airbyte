/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.standardtest.destination;

import io.airbyte.cdk.integrations.base.FailureTrackingAirbyteMessageConsumer;
import io.airbyte.cdk.protocol.PartialAirbyteMessage;
import io.airbyte.cdk.protocol.PartialAirbyteStateMessage;
import io.airbyte.cdk.protocol.PartialAirbyteStreamState;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.function.Consumer;
import org.junit.jupiter.api.Test;
import org.mockito.InOrder;
import org.mockito.Mockito;

public abstract class PerStreamStateMessageTest {

  protected abstract Consumer<AirbyteMessage> getMockedConsumer();

  protected abstract FailureTrackingAirbyteMessageConsumer getMessageConsumer();

  @Test
  void ensureAllStateMessageAreEmitted() throws Exception {
    final PartialAirbyteMessage airbyteMessage1 = AirbyteMessageCreator.createStreamStateMessage("name_one", "state_one");
    final PartialAirbyteMessage airbyteMessage2 = AirbyteMessageCreator.createStreamStateMessage("name_two", "state_two");
    final PartialAirbyteMessage airbyteMessage3 = AirbyteMessageCreator.createStreamStateMessage("name_three", "state_three");
    final FailureTrackingAirbyteMessageConsumer messageConsumer = getMessageConsumer();

    messageConsumer.accept(airbyteMessage1);
    messageConsumer.accept(airbyteMessage2);
    messageConsumer.accept(airbyteMessage3);

    final Consumer<AirbyteMessage> mConsumer = getMockedConsumer();
    final InOrder inOrder = Mockito.inOrder(mConsumer);

    inOrder.verify(mConsumer).accept(airbyteMessage1.toFullMessage());
    inOrder.verify(mConsumer).accept(airbyteMessage2.toFullMessage());
    inOrder.verify(mConsumer).accept(airbyteMessage3.toFullMessage());
  }

  class AirbyteMessageCreator {

    public static PartialAirbyteMessage createStreamStateMessage(final String name, final String value) {
      return new PartialAirbyteMessage()
          .withType(Type.STATE)
          .withState(
              new PartialAirbyteStateMessage()
                  .withType(AirbyteStateType.STREAM)
                  .withStream(
                      new PartialAirbyteStreamState()
                          .withStreamDescriptor(
                              new StreamDescriptor()
                                  .withName(name))
                          .withStreamState(Jsons.jsonNode(value))));
    }

  }

}
