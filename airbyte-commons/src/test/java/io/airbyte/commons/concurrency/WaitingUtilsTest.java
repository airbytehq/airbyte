/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.concurrency;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.time.Duration;
import java.util.function.Supplier;
import org.junit.jupiter.api.Test;

class WaitingUtilsTest {

  @SuppressWarnings("unchecked")
  @Test
  void testWaitForConditionConditionMet() {
    final Supplier<Boolean> condition = mock(Supplier.class);
    when(condition.get())
        .thenReturn(false)
        .thenReturn(false)
        .thenReturn(true);
    assertTrue(WaitingUtils.waitForCondition(Duration.ofMillis(1), Duration.ofMillis(5), condition));
  }

  @SuppressWarnings("unchecked")
  @Test
  void testWaitForConditionTimeout() {
    final Supplier<Boolean> condition = mock(Supplier.class);
    when(condition.get()).thenReturn(false);
    assertFalse(WaitingUtils.waitForCondition(Duration.ofMillis(1), Duration.ofMillis(5), condition));
  }

}
