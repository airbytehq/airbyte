/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import io.airbyte.config.Schedule;
import java.util.concurrent.TimeUnit;

public class ScheduleHelpers {

  public static Long getSecondsInUnit(Schedule.TimeUnit timeUnitEnum) {
    switch (timeUnitEnum) {
      case MINUTES:
        return TimeUnit.MINUTES.toSeconds(1);
      case HOURS:
        return TimeUnit.HOURS.toSeconds(1);
      case DAYS:
        return TimeUnit.DAYS.toSeconds(1);
      case WEEKS:
        return TimeUnit.DAYS.toSeconds(1) * 7;
      case MONTHS:
        return TimeUnit.DAYS.toSeconds(1) * 30;
      default:
        throw new RuntimeException("Unhandled TimeUnitEnum: " + timeUnitEnum);
    }
  }

  public static Long getIntervalInSecond(Schedule schedule) {
    return getSecondsInUnit(schedule.getTimeUnit()) * schedule.getUnits();
  }

}
