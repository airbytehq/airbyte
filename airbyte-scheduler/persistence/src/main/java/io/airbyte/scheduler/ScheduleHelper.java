/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler;

import com.cronutils.model.Cron;
import com.cronutils.model.CronType;
import com.cronutils.model.definition.CronDefinition;
import com.cronutils.model.definition.CronDefinitionBuilder;
import com.cronutils.model.time.ExecutionTime;
import com.cronutils.parser.CronParser;
import java.time.ZonedDateTime;

public class ScheduleHelper {

  private static final CronDefinition DEFINITION = CronDefinitionBuilder.instanceDefinitionFor(CronType.UNIX);
  private static final CronParser PARSER = new CronParser(DEFINITION);

  public static Cron validateCron(String cronSchedule) {
    var cron = PARSER.parse(cronSchedule);
    cron.validate();
    return cron;
  }

  public static long nextExecutionTime(String cronSchedule) {
    // very high value default, indicates no next execution time.
    var next = Long.MAX_VALUE;
    var cron = validateCron(cronSchedule);
    var timer = ExecutionTime.forCron(cron);
    var time = timer.nextExecution(ZonedDateTime.now());
    if (time.isPresent()) {
      next = time.get().toEpochSecond();
    }
    return next;
  }

  public static long intervalInSeconds(String cronSchedule) {
    var interval = Long.MAX_VALUE;
    var cron = validateCron(cronSchedule);
    var timer = ExecutionTime.forCron(cron);
    var time = timer.nextExecution(ZonedDateTime.now());
    if (time.isPresent()) {
      var next = time.get();
      var afterNext = timer.nextExecution(next);
      if (afterNext.isPresent()) {
        // interval in mins
        interval = (afterNext.get().toEpochSecond() - next.toEpochSecond());
      }
    }
    return interval;
  }

  public static long intervalInMinutes(String cronSchedule) {
    return intervalInSeconds(cronSchedule) / 60;
  }

}
