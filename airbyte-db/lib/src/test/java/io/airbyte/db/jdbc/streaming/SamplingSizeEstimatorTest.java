/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import static org.junit.jupiter.api.Assertions.*;

import java.util.Optional;
import org.junit.jupiter.api.Test;

class SamplingSizeEstimatorTest {

  @Test
  public void testIt() {
    final long bufferByteSize = 120;
    final int sampleSize = 2;
    final int sampleFrequency = 3;
    final long initialByteSize = 30;
    final int minFetchSize = 1;
    final int defaultFetchSize = 20;
    final int maxFetchSize = 120;
    final SamplingSizeEstimator sizeEstimator = new SamplingSizeEstimator(
        bufferByteSize,
        sampleSize,
        sampleFrequency,
        initialByteSize,
        minFetchSize,
        defaultFetchSize,
        maxFetchSize);

    double meanByteSize = initialByteSize;

    // size: 3 * 4 = 12, not sampled
    sizeEstimator.accept("1");
    assertFalse(sizeEstimator.getFetchSize().isPresent());
    assertEquals(meanByteSize, sizeEstimator.getMeanRowByteSize());

    // size: 4 * 4 = 16, not sampled
    sizeEstimator.accept("11");
    assertFalse(sizeEstimator.getFetchSize().isPresent());
    assertEquals(meanByteSize, sizeEstimator.getMeanRowByteSize());

    // size: 5 * 4 = 20, sampled, fetch size is ready
    sizeEstimator.accept("111");
    final Optional<Integer> fetchSize1 = sizeEstimator.getFetchSize();
    assertTrue(fetchSize1.isPresent());
    meanByteSize = (meanByteSize + 20) / 2.0;
    assertDoubleEquals(meanByteSize, sizeEstimator.getMeanRowByteSize());
    assertDoubleEquals(bufferByteSize / meanByteSize, fetchSize1.get().doubleValue());

    // size: 6 * 4 = 24, not sampled
    sizeEstimator.accept("1111");
    assertFalse(sizeEstimator.getFetchSize().isPresent());
    assertDoubleEquals(meanByteSize, sizeEstimator.getMeanRowByteSize());

    // size: 7 * 4 = 28, not sampled
    sizeEstimator.accept("11111");
    assertFalse(sizeEstimator.getFetchSize().isPresent());
    assertDoubleEquals(meanByteSize, sizeEstimator.getMeanRowByteSize());

    // size: 8 * 4 = 32, sampled, fetch size is ready
    sizeEstimator.accept("111111");
    final Optional<Integer> fetchSize2 = sizeEstimator.getFetchSize();
    assertTrue(fetchSize2.isPresent());
    meanByteSize = (meanByteSize + 32) / 2.0;
    assertDoubleEquals(meanByteSize, sizeEstimator.getMeanRowByteSize());
    assertDoubleEquals(bufferByteSize / meanByteSize, fetchSize2.get().doubleValue());
  }

  private static void assertDoubleEquals(final double expected, final double actual) {
    assertEquals(Math.round(expected), Math.round(actual));
  }

}
