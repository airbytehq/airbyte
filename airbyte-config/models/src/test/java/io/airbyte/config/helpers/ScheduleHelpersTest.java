/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.airbyte.config.Schedule;
import java.util.Arrays;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class ScheduleHelpersTest {

  @Test
  void testGetSecondsInUnit() {
    assertEquals(60, ScheduleHelpers.getSecondsInUnit(Schedule.TimeUnit.MINUTES));
    assertEquals(3600, ScheduleHelpers.getSecondsInUnit(Schedule.TimeUnit.HOURS));
    assertEquals(86_400, ScheduleHelpers.getSecondsInUnit(Schedule.TimeUnit.DAYS));
    assertEquals(604_800, ScheduleHelpers.getSecondsInUnit(Schedule.TimeUnit.WEEKS));
    assertEquals(2_592_000, ScheduleHelpers.getSecondsInUnit(Schedule.TimeUnit.MONTHS));
  }

  // Will throw if a new TimeUnit is added but an appropriate mapping is not included in this method.
  @Test
  void testAllOfTimeUnitEnumValues() {
    Arrays.stream(Schedule.TimeUnit.values()).forEach(ScheduleHelpers::getSecondsInUnit);
  }

}
