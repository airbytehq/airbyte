/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import static org.junit.jupiter.api.Assertions.*;

import java.util.Optional;
import org.junit.jupiter.api.Test;

class SamplingSizeEstimatorTest {

  @Test
  void testIt() {
    final long bufferByteSize = 120;
    final int sampleFrequency = 3;
    final long initialByteSize = 10;
    final int minFetchSize = 1;
    final int defaultFetchSize = 20;
    final int maxFetchSize = 120;
    final SamplingSizeEstimator sizeEstimator = new SamplingSizeEstimator(
        bufferByteSize,
        sampleFrequency,
        initialByteSize,
        minFetchSize,
        defaultFetchSize,
        maxFetchSize);

    double maxByteSize = initialByteSize;

    // size: 3 * 4 = 12, not sampled
    sizeEstimator.accept("1");
    assertFalse(sizeEstimator.getFetchSize().isPresent());
    assertEquals(maxByteSize, sizeEstimator.getMaxRowByteSize());

    // size: 4 * 4 = 16, not sampled
    sizeEstimator.accept("11");
    assertFalse(sizeEstimator.getFetchSize().isPresent());
    assertEquals(maxByteSize, sizeEstimator.getMaxRowByteSize());

    // size: 5 * 4 = 20, sampled, fetch size is ready
    sizeEstimator.accept("111");
    final Optional<Integer> fetchSize1 = sizeEstimator.getFetchSize();
    maxByteSize = 20;
    assertDoubleEquals(20, sizeEstimator.getMaxRowByteSize());
    assertDoubleEquals(bufferByteSize / maxByteSize, fetchSize1.get().doubleValue());

    // size: 6 * 4 = 24, not sampled
    sizeEstimator.accept("1111");
    assertFalse(sizeEstimator.getFetchSize().isPresent());
    assertDoubleEquals(maxByteSize, sizeEstimator.getMaxRowByteSize());

    // size: 7 * 4 = 28, not sampled
    sizeEstimator.accept("11111");
    assertFalse(sizeEstimator.getFetchSize().isPresent());
    assertDoubleEquals(maxByteSize, sizeEstimator.getMaxRowByteSize());

    // size: 8 * 4 = 32, sampled, fetch size is ready
    sizeEstimator.accept("111111");
    final Optional<Integer> fetchSize2 = sizeEstimator.getFetchSize();
    assertTrue(fetchSize2.isPresent());
    maxByteSize = 32;
    assertDoubleEquals(maxByteSize, sizeEstimator.getMaxRowByteSize());
    assertDoubleEquals(bufferByteSize / maxByteSize, fetchSize2.get().doubleValue());
  }

  private static void assertDoubleEquals(final double expected, final double actual) {
    assertEquals(Math.round(expected), Math.round(actual));
  }

}
