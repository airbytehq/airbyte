/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import static org.junit.jupiter.api.Assertions.*;

import java.util.Optional;
import org.junit.jupiter.api.Test;

class InitialSizeEstimatorTest {

  @Test
  public void testIt() {
    final long bufferByteSize = 120;
    final int initialSampleSize = 5;
    final int minFetchSize = 1;
    final int defaultFetchSize = 20;
    final int maxFetchSize = 120;
    final InitialSizeEstimator sizeEstimator = new InitialSizeEstimator(
        bufferByteSize,
        initialSampleSize,
        minFetchSize,
        defaultFetchSize,
        maxFetchSize);

    // size: 3 * 4 = 12
    sizeEstimator.accept("1");
    assertFalse(sizeEstimator.getFetchSize().isPresent());
    // size: 4 * 4 = 16
    sizeEstimator.accept("11");
    assertFalse(sizeEstimator.getFetchSize().isPresent());
    // size: 5 * 4 = 20
    sizeEstimator.accept("111");
    assertFalse(sizeEstimator.getFetchSize().isPresent());
    // size: 6 * 4 = 24
    sizeEstimator.accept("1111");
    assertFalse(sizeEstimator.getFetchSize().isPresent());
    // size: 7 * 4 = 28, fetch size is available
    sizeEstimator.accept("11111");
    final Optional<Integer> fetchSize = sizeEstimator.getFetchSize();
    assertTrue(fetchSize.isPresent());
    final long expectedMeanByteSize = 20L;
    assertEquals(expectedMeanByteSize, Math.round(sizeEstimator.getMeanRowByteSize()));
    assertEquals(bufferByteSize / expectedMeanByteSize, fetchSize.get().longValue());
  }

}
