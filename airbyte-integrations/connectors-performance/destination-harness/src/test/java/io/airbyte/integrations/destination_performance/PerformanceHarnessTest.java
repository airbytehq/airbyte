/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_performance;

import static org.junit.Assert.assertNotEquals;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;
import org.junit.jupiter.api.Test;

class PerformanceHarnessTest {

  @Test
  public void testRandomStreamName() {
    final List<String> streamNames = new ArrayList<>();
    final Random random = new Random();
    final int duplicateFactor = 1000;
    // Keep this number high to avoid statistical collisions. Alternative was to consider chi-squared
    for (int i = 1; i <= duplicateFactor; i++) {
      streamNames.add("stream" + i);
    }
    final String streamName1 = PerformanceHarness.getStreamName(streamNames, random);
    final String streamName2 = PerformanceHarness.getStreamName(streamNames, random);
    assertNotEquals(streamName1, streamName2);
  }

}
