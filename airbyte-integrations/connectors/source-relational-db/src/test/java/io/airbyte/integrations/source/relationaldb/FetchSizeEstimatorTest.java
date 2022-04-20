/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.relationaldb;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class FetchSizeEstimatorTest {

  @Test
  public void testGetFetchSize() {
    final long fetchBufferBytes = 100L;
    final int defaultSize = 10;
    final int minSize = 5;
    final int maxSize = 20;
    final FetchSizeEstimator estimator = new FetchSizeEstimator(fetchBufferBytes, minSize, defaultSize, maxSize);

    // default size
    assertEquals(defaultSize, estimator.getFetchSize(-1L));
    assertEquals(defaultSize, estimator.getFetchSize(0L));

    // min size
    assertEquals(minSize, estimator.getFetchSize(100L));
    assertEquals(minSize, estimator.getFetchSize(200L));

    // max size
    assertEquals(maxSize, estimator.getFetchSize(1L));
    assertEquals(maxSize, estimator.getFetchSize(2L));

    // buffer bytes / row bytes
    assertEquals(12, estimator.getFetchSize(8L));
    assertEquals(11, estimator.getFetchSize(9L));
    assertEquals(10, estimator.getFetchSize(10L));
  }

}
