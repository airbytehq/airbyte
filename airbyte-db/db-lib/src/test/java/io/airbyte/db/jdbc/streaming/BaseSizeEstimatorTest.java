/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import static org.junit.jupiter.api.Assertions.*;

import io.airbyte.commons.json.Jsons;
import java.util.Map;
import java.util.Optional;
import org.junit.jupiter.api.Test;

class BaseSizeEstimatorTest {

  @Test
  void testGetEstimatedByteSize() {
    assertEquals(0L, BaseSizeEstimator.getEstimatedByteSize(null));
    assertEquals(21L, BaseSizeEstimator.getEstimatedByteSize("12345"));
    assertEquals(45L, BaseSizeEstimator.getEstimatedByteSize(Jsons.jsonNode(Map.of("key", "value"))));
  }

  public static class TestSizeEstimator extends BaseSizeEstimator {

    protected TestSizeEstimator(final long bufferByteSize, final int minFetchSize, final int defaultFetchSize, final int maxFetchSize) {
      super(bufferByteSize, minFetchSize, defaultFetchSize, maxFetchSize);
    }

    @Override
    public Optional<Integer> getFetchSize() {
      return Optional.empty();
    }

    @Override
    public void accept(final Object o) {}

    public void setMeanByteSize(final double meanByteSize) {
      this.maxRowByteSize = meanByteSize;
    }

  }

  @Test
  void testGetBoundedFetchSize() {
    final long bufferByteSize = 120;
    final int minFetchSize = 10;
    final int defaultFetchSize = 20;
    final int maxFetchSize = 40;
    final TestSizeEstimator sizeEstimator = new TestSizeEstimator(bufferByteSize, minFetchSize, defaultFetchSize, maxFetchSize);

    sizeEstimator.setMeanByteSize(-1.0);
    assertEquals(defaultFetchSize, sizeEstimator.getBoundedFetchSize());

    sizeEstimator.setMeanByteSize(0.0);
    assertEquals(defaultFetchSize, sizeEstimator.getBoundedFetchSize());

    // fetch size = 5 < min fetch size
    sizeEstimator.setMeanByteSize(bufferByteSize / 5.0);
    assertEquals(minFetchSize, sizeEstimator.getBoundedFetchSize());

    // fetch size = 10 within [min fetch size, max fetch size]
    sizeEstimator.setMeanByteSize(bufferByteSize / 10.0);
    assertEquals(10, sizeEstimator.getBoundedFetchSize());

    // fetch size = 30 within [min fetch size, max fetch size]
    sizeEstimator.setMeanByteSize(bufferByteSize / 30.0);
    assertEquals(30, sizeEstimator.getBoundedFetchSize());

    // fetch size = 40 within [min fetch size, max fetch size]
    sizeEstimator.setMeanByteSize(bufferByteSize / 40.0);
    assertEquals(40, sizeEstimator.getBoundedFetchSize());

    // fetch size = 60 > max fetch size
    sizeEstimator.setMeanByteSize(bufferByteSize / 60.0);
    assertEquals(maxFetchSize, sizeEstimator.getBoundedFetchSize());
  }

}
