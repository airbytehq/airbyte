/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import org.junit.jupiter.api.Test;

class SpeedBenchmarkGeneratorIteratorTest {

  @Test
  void computeRandomStringIsDeterministic() {
    final SpeedBenchmarkGeneratorIterator iter = new SpeedBenchmarkGeneratorIterator(1);
    final SpeedBenchmarkGeneratorIterator iter2 = new SpeedBenchmarkGeneratorIterator(1);

    final JsonNode data = iter.next().getRecord().getData();
    final JsonNode data2 = iter2.next().getRecord().getData();

    assertEquals(data, data2);
  }

  @Test
  void computeRandomStringIsDifferentBetweenIterations() {
    final SpeedBenchmarkGeneratorIterator iter = new SpeedBenchmarkGeneratorIterator(2);
    final SpeedBenchmarkGeneratorIterator iter2 = new SpeedBenchmarkGeneratorIterator(2);

    // Confirms that data is the same
    final JsonNode data = iter.next().getRecord().getData();
    final JsonNode data2 = iter2.next().getRecord().getData();
    assertEquals(data, data2);

    final JsonNode dataNext = iter.next().getRecord().getData();
    final JsonNode data2Next = iter2.next().getRecord().getData();

    // Confirms that data between each iteration isn't the same but they are still deterministic within
    // the same iteration
    assertNotEquals(data, dataNext);
    assertEquals(dataNext, data2Next);
  }

}
