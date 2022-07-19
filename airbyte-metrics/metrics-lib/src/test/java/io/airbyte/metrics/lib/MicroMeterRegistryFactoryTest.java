/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.metrics.lib;

import static org.junit.jupiter.api.Assertions.*;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class MicroMeterRegistryFactoryTest {

  @Test
  @DisplayName("Should not return null if metric client not specified;")
  public void testMicroMeterRegistryRuturnsNullForEmptyClientConfig() {
    assertNull(MicroMeterRegistryFactory.getMeterRegistry());
  }

}
