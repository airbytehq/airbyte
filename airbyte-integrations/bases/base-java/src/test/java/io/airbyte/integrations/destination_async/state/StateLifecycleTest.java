/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.state;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.util.Optional;
import org.junit.jupiter.api.Test;

class StateLifecycleTest {

  @SuppressWarnings("OptionalGetWithoutIsPresent")
  @Test
  void testLifecycle() {
    final StateLifecycle lifecycle = new StateLifecycle();

    lifecycle.trackState(createState(100), 100);
    lifecycle.trackState(createState(200), 200);
    lifecycle.trackState(createState(300), 300);
    lifecycle.trackState(createState(400), 400);

    assertEquals(Optional.empty(), lifecycle.getBestStateAndPurge(50));

    assertEquals(100, getStateMessageIdentifier(lifecycle.getBestStateAndPurge(150).get()));

    lifecycle.trackState(createState(500), 500);

    assertEquals(400, getStateMessageIdentifier(lifecycle.getBestStateAndPurge(425).get()));
    assertEquals(500, getStateMessageIdentifier(lifecycle.getBestStateAndPurge(500).get()));

    assertEquals(Optional.empty(), lifecycle.getBestStateAndPurge(550));
  }

  /*
   * shortcut for the sake of the test to just reuse the message number as the contents of the state
   * message to identify it.
   */
  private AirbyteMessage createState(final long messageNum) {
    return new AirbyteMessage().withState(new AirbyteStateMessage().withData(Jsons.jsonNode(messageNum)));
  }

  private long getStateMessageIdentifier(final AirbyteMessage message) {
    return message.getState().getData().asLong();
  }

}
