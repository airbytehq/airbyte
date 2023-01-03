/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.helpers;

import io.airbyte.config.BasicSchedule;
import io.airbyte.config.Schedule;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.ScheduleType;
import java.util.concurrent.TimeUnit;

@SuppressWarnings("PMD.AvoidThrowingRawExceptionTypes")
public class ScheduleHelpers {

  public static Long getSecondsInUnit(final Schedule.TimeUnit timeUnitEnum) {
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

  public static Long getSecondsInUnit(final BasicSchedule.TimeUnit timeUnitEnum) {
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

  public static Long getIntervalInSecond(final Schedule schedule) {
    return getSecondsInUnit(schedule.getTimeUnit()) * schedule.getUnits();
  }

  public static Long getIntervalInSecond(final BasicSchedule schedule) {
    return getSecondsInUnit(schedule.getTimeUnit()) * schedule.getUnits();
  }

  public static boolean isScheduleTypeMismatch(final StandardSync standardSync) {
    if (standardSync.getScheduleType() == null) {
      return false;
    }
    return (standardSync.getManual() && standardSync.getScheduleType() != ScheduleType.MANUAL) || (!standardSync.getManual()
        && standardSync.getScheduleType() == ScheduleType.MANUAL);
  }

}
