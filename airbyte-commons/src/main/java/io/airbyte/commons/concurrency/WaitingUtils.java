/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.concurrency;

import static java.lang.Thread.sleep;

import java.time.Duration;
import java.util.function.Supplier;

public class WaitingUtils {

  /**
   * Wait for a condition or timeout.
   *
   * @param interval - frequency with which condition and timeout should be checked.
   * @param timeout - how long to wait in total
   * @param condition - supplier that returns whether the condition has been met.
   * @return true if condition was met before the timeout was reached, otherwise false.
   */
  @SuppressWarnings("BusyWait")
  public static boolean waitForCondition(final Duration interval, final Duration timeout, final Supplier<Boolean> condition) {
    Duration timeWaited = Duration.ZERO;
    while (true) {
      if (condition.get()) {
        return true;
      }

      if (timeout.minus(timeWaited).isNegative()) {
        return false;
      }

      try {
        sleep(interval.toMillis());
      } catch (final InterruptedException e) {
        throw new RuntimeException(e);
      }

      timeWaited = timeWaited.plus(interval);
    }
  }

}
