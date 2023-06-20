/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.kafka.state;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import java.io.IOException;
import java.util.Map;
import org.apache.kafka.common.TopicPartition;
import org.junit.jupiter.api.Test;

public class StateHelperTest {

  @Test
  public void testGlobalStateDeserialisation() throws IOException {
    final var jsonState = Jsons.deserialize(MoreResources.readResource("state/test_global_state_deserialisation.json"));
    final var state = StateHelper.stateFromJson(jsonState);
    final var expected = Map.ofEntries(
        Map.entry(new TopicPartition("topic-0", 0), 42L)
    );
    assertEquals(expected, state);
  }

  @Test
  public void testLegacyStateDeserialisation() throws IOException {
    final var jsonState = Jsons.deserialize(MoreResources.readResource("state/test_legacy_state_deserialisation.json"));
    final var state = StateHelper.stateFromJson(jsonState);
    assertTrue(state.isEmpty());
  }

  @Test
  public void testStreamStateDeserialisation() throws IOException {
    final var jsonState = Jsons.deserialize(MoreResources.readResource("state/test_stream_state_deserialisation.json"));
    final var state = StateHelper.stateFromJson(jsonState);
    final var expected = Map.ofEntries(
        Map.entry(new TopicPartition("topic-1", 0), 24L),
        Map.entry(new TopicPartition("topic-1", 1), 42L)
    );
    assertEquals(expected, state);
  }

  @Test
  public void testStateSerialisation() throws IOException {
    final var state = Map.ofEntries(
        Map.entry(new TopicPartition("topic-0", 0), 24L),
        Map.entry(new TopicPartition("topic-1", 0), 42L),
        Map.entry(new TopicPartition("topic-1", 1), 66L)
    );
    final var serialised = Jsons.serialize(StateHelper.toAirbyteState(state));
    final var expected = MoreResources.readResource("state/test_state_serialisation.json");
    assertEquals(expected, serialised);
  }

}

