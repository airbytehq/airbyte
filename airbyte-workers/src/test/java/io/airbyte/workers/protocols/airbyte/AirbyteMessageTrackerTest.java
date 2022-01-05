/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.base.Charsets;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import io.airbyte.protocol.models.AirbyteStateMessage;
import org.junit.jupiter.api.Test;

class AirbyteMessageTrackerTest {

  @Test
  public void testIncrementsWhenRecord() {
    final AirbyteMessage message = new AirbyteMessage()
        .withType(AirbyteMessage.Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withData(Jsons.jsonNode(ImmutableMap.of("name", "rudolph"))));

    final AirbyteMessageTracker messageTracker = new AirbyteMessageTracker();
    messageTracker.acceptFromSource(message);
    messageTracker.acceptFromSource(message);
    messageTracker.acceptFromSource(message);

    assertEquals(3, messageTracker.getTotalRecordsEmitted());
    assertEquals(3 * Jsons.serialize(message.getRecord().getData()).getBytes(Charsets.UTF_8).length, messageTracker.getTotalBytesEmitted());
  }

  @Test
  public void testRetainsLatestSourceState() {
    final JsonNode oldStateValue = Jsons.jsonNode(ImmutableMap.builder().put("lastSync", "1598900000").build());
    final AirbyteMessage oldStateMessage = new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(oldStateValue));

    final JsonNode newStateValue = Jsons.jsonNode(ImmutableMap.builder().put("lastSync", "1598993526").build());
    final AirbyteMessage newStateMessage = new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(newStateValue));

    final AirbyteMessageTracker messageTracker = new AirbyteMessageTracker();
    messageTracker.acceptFromSource(oldStateMessage);
    messageTracker.acceptFromSource(oldStateMessage);
    messageTracker.acceptFromSource(newStateMessage);

    assertTrue(messageTracker.getSourceOutputState().isPresent());
    assertEquals(new State().withState(newStateValue), messageTracker.getSourceOutputState().get());
  }

  // TODO parker: dry up?
  @Test
  public void testRetainsLatestDestinationState() {
    final JsonNode oldStateValue = Jsons.jsonNode(ImmutableMap.builder().put("lastSync", "1598900000").build());
    final AirbyteMessage oldStateMessage = new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(oldStateValue));

    final JsonNode newStateValue = Jsons.jsonNode(ImmutableMap.builder().put("lastSync", "1598993526").build());
    final AirbyteMessage newStateMessage = new AirbyteMessage()
        .withType(AirbyteMessage.Type.STATE)
        .withState(new AirbyteStateMessage().withData(newStateValue));

    final AirbyteMessageTracker messageTracker = new AirbyteMessageTracker();
    messageTracker.acceptFromDestination(oldStateMessage);
    messageTracker.acceptFromDestination(oldStateMessage);
    messageTracker.acceptFromDestination(newStateMessage);

    assertTrue(messageTracker.getDestinationOutputState().isPresent());
    assertEquals(new State().withState(newStateValue), messageTracker.getDestinationOutputState().get());
  }

  @Test
  public void testReturnEmptyStateIfNoneEverAccepted() {
    final AirbyteMessageTracker MessageTracker = new AirbyteMessageTracker();
    assertTrue(MessageTracker.getSourceOutputState().isEmpty());
    assertTrue(MessageTracker.getDestinationOutputState().isEmpty());
  }

  @Test
  public void hashStuff() {
    // final AirbyteMessageTracker messageTracker = new AirbyteMessageTracker();
    //
    // final AirbyteMessage stateMessage = new AirbyteMessage().withType(Type.STATE).withState(
    // new AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.builder().put("checkpoint",
    // 20).build())));
    //
    // final AirbyteStateMessage state = stateMessage.getState();
    //
    // final int hashcode =
    // Hashing.murmur3_32_fixed().hashBytes(Jsons.serialize(state.getData()).getBytes(Charsets.UTF_8)).hashCode();
    //
    // assertTrue(true);
    //
    // final ConcurrentLinkedQueue<Integer> queue = new ConcurrentLinkedQueue<>();
    // final Iterator<Integer> queueIter = queue.;
    // queue.add(1);
    // System.out.println(queueIter.next());
    // queue.add(2);
    // queue.add(3);
    // assertTrue(true);

  }

}
