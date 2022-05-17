/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc.streaming;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.Test;

class TwoStageSizeEstimatorTest {

  @Test
  public void testDelegationSwitch() {
    final TwoStageSizeEstimator sizeEstimator = TwoStageSizeEstimator.getInstance();
    for (int i = 0; i < FetchSizeConstants.INITIAL_SAMPLE_SIZE; ++i) {
      sizeEstimator.accept("1");
      assertTrue(sizeEstimator.getDelegate() instanceof InitialSizeEstimator);
    }
    // delegation is changed after initial sampling
    for (int i = 0; i < 3; ++i) {
      sizeEstimator.accept("1");
      assertTrue(sizeEstimator.getDelegate() instanceof SamplingSizeEstimator);
    }
  }

}
