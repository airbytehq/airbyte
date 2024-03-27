/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.cdk.integrations.base.DestinationConfig;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import java.util.concurrent.atomic.AtomicLong;
import java.util.function.Supplier;
import java.util.stream.IntStream;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

public class TypeAndDedupeOperationValveTest {

  private static final AirbyteStreamNameNamespacePair STREAM_A = new AirbyteStreamNameNamespacePair("a", "a");
  private static final AirbyteStreamNameNamespacePair STREAM_B = new AirbyteStreamNameNamespacePair("b", "b");
  private static final Supplier<Long> ALWAYS_ZERO = () -> 0l;

  private Supplier<Long> minuteUpdates;

  @BeforeEach
  public void setup() {
    AtomicLong start = new AtomicLong(0);
    minuteUpdates = () -> start.getAndUpdate(l -> l + (60 * 1000));
  }

  @AfterEach
  public void clearDestinationConfig() {
    DestinationConfig.clearInstance();
  }

  private void initializeDestinationConfigOption(final boolean enableIncrementalTypingAndDeduping) {
    ObjectMapper mapper = new ObjectMapper();
    ObjectNode objectNode = mapper.createObjectNode();
    objectNode.put("enable_incremental_final_table_updates", enableIncrementalTypingAndDeduping);
    DestinationConfig.initialize(objectNode);
  }

  private void elapseTime(Supplier<Long> timing, int iterations) {
    IntStream.range(0, iterations).forEach(__ -> {
      timing.get();
    });
  }

  @ParameterizedTest
  @ValueSource(booleans = {true, false})
  public void testAddStream(final boolean enableIncrementalTypingAndDeduping) {
    initializeDestinationConfigOption(enableIncrementalTypingAndDeduping);
    final var valve = new TypeAndDedupeOperationValve(ALWAYS_ZERO);
    valve.addStream(STREAM_A);
    Assertions.assertEquals(-1, valve.getIncrementInterval(STREAM_A));
    Assertions.assertEquals(valve.readyToTypeAndDedupe(STREAM_A), enableIncrementalTypingAndDeduping);
    Assertions.assertEquals(valve.get(STREAM_A), 0l);
  }

  @ParameterizedTest
  @ValueSource(booleans = {true, false})
  public void testReadyToTypeAndDedupe(final boolean enableIncrementalTypingAndDeduping) {
    initializeDestinationConfigOption(enableIncrementalTypingAndDeduping);
    final var valve = new TypeAndDedupeOperationValve(minuteUpdates);
    // method call increments time
    valve.addStream(STREAM_A);
    elapseTime(minuteUpdates, 1);
    // method call increments time
    valve.addStream(STREAM_B);
    // method call increments time
    Assertions.assertEquals(valve.readyToTypeAndDedupe(STREAM_A), enableIncrementalTypingAndDeduping);
    elapseTime(minuteUpdates, 1);
    Assertions.assertEquals(valve.readyToTypeAndDedupe(STREAM_B), enableIncrementalTypingAndDeduping);
    valve.updateTimeAndIncreaseInterval(STREAM_A);
    Assertions.assertEquals(1000 * 60 * 60 * 6,
        valve.getIncrementInterval(STREAM_A));
    // method call increments time
    Assertions.assertFalse(valve.readyToTypeAndDedupe(STREAM_A));
    // More than enough time has passed now
    elapseTime(minuteUpdates, 60 * 6);
    Assertions.assertEquals(valve.readyToTypeAndDedupe(STREAM_A), enableIncrementalTypingAndDeduping);
  }

  @ParameterizedTest
  @ValueSource(booleans = {true, false})
  public void testUpdateTimeAndIncreaseInterval(final boolean enableIncrementalTypingAndDeduping) {
    initializeDestinationConfigOption(enableIncrementalTypingAndDeduping);
    final var valve = new TypeAndDedupeOperationValve(minuteUpdates);
    valve.addStream(STREAM_A);
    IntStream.range(0, 1).forEach(__ -> Assertions.assertEquals(valve.readyToTypeAndDedupe(STREAM_A), enableIncrementalTypingAndDeduping)); // start
                                                                                                                                            // ready
                                                                                                                                            // to T&D
    Assertions.assertEquals(valve.readyToTypeAndDedupe(STREAM_A), enableIncrementalTypingAndDeduping);
    valve.updateTimeAndIncreaseInterval(STREAM_A);
    IntStream.range(0, 360).forEach(__ -> Assertions.assertFalse(valve.readyToTypeAndDedupe(STREAM_A)));
    Assertions.assertEquals(valve.readyToTypeAndDedupe(STREAM_A), enableIncrementalTypingAndDeduping);
  }

}
