/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.nebulagraph;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.util.List;
import java.util.Map;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

@DisplayName("VidGenerator")
class VidGeneratorTest {

  @Test
  void buildVidHappyPathMultipleFieldsAndSeparator() {
    VidGenerator gen = new VidGenerator();
    Map<String, Object> record = Map.of(
        "tenant_id", "t1",
        "user_id", "u99",
        "suffix", 7);

    String vid = gen.buildVid(record, List.of("tenant_id", "user_id", "suffix"), "::", 128);
    assertEquals("t1::u99::7", vid);
  }

  @Test
  void buildVidMissingFieldThrows() {
    VidGenerator gen = new VidGenerator();
    Map<String, Object> record = Map.of("tenant_id", "t1");

    assertThrows(IllegalArgumentException.class,
        () -> gen.buildVid(record, List.of("tenant_id", "user_id"), "::", 128));
  }

  @Test
  void buildVidExceedsMaxLenThrows() {
    VidGenerator gen = new VidGenerator();
    Map<String, Object> record = Map.of("a", "x".repeat(10), "b", "y".repeat(10));

    assertThrows(IllegalArgumentException.class,
        () -> gen.buildVid(record, List.of("a", "b"), ":", 5));
  }

}
