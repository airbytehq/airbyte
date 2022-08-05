/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.handlers;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.airbyte.api.model.generated.ConnectionScheduleData;
import io.airbyte.api.model.generated.ConnectionScheduleDataBasicSchedule;
import io.airbyte.api.model.generated.ConnectionScheduleDataBasicSchedule.TimeUnitEnum;
import io.airbyte.api.model.generated.ConnectionScheduleDataCron;
import io.airbyte.api.model.generated.ConnectionScheduleType;
import io.airbyte.config.BasicSchedule.TimeUnit;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.ScheduleType;
import io.airbyte.server.handlers.helpers.ConnectionScheduleHelper;
import io.airbyte.validation.json.JsonValidationException;
import org.junit.jupiter.api.Test;

class ConnectionSchedulerHelperTest {

  private final static String EXPECTED_CRON_TIMEZONE = "UTC";
  private final static String EXPECTED_CRON_EXPRESSION = "* */2 * * * ?";

  @Test
  void testPopulateSyncScheduleFromManualType() throws JsonValidationException {
    final StandardSync actual = new StandardSync();
    ConnectionScheduleHelper.populateSyncFromScheduleTypeAndData(actual,
        ConnectionScheduleType.MANUAL, null);
    assertTrue(actual.getManual());
    assertEquals(ScheduleType.MANUAL, actual.getScheduleType());
    assertNull(actual.getSchedule());
    assertNull(actual.getScheduleData());
  }

  @Test
  void testPopulateSyncScheduleFromBasicType() throws JsonValidationException {
    final StandardSync actual = new StandardSync();
    ConnectionScheduleHelper.populateSyncFromScheduleTypeAndData(actual,
        ConnectionScheduleType.BASIC, new ConnectionScheduleData()
            .basicSchedule(new ConnectionScheduleDataBasicSchedule()
                .timeUnit(TimeUnitEnum.HOURS)
                .units(1L)));
    assertFalse(actual.getManual());
    assertEquals(ScheduleType.BASIC_SCHEDULE, actual.getScheduleType());
    assertEquals(TimeUnit.HOURS, actual.getScheduleData().getBasicSchedule().getTimeUnit());
    assertEquals(1L, actual.getScheduleData().getBasicSchedule().getUnits());
    assertNull(actual.getSchedule());
  }

  @Test
  void testPopulateSyncScheduleFromCron() throws JsonValidationException {
    final StandardSync actual = new StandardSync();
    ConnectionScheduleHelper.populateSyncFromScheduleTypeAndData(actual,
        ConnectionScheduleType.CRON, new ConnectionScheduleData()
            .cron(new ConnectionScheduleDataCron()
                .cronTimeZone(EXPECTED_CRON_TIMEZONE)
                .cronExpression(EXPECTED_CRON_EXPRESSION)));
    assertEquals(ScheduleType.CRON, actual.getScheduleType());
    assertEquals(EXPECTED_CRON_TIMEZONE, actual.getScheduleData().getCron().getCronTimeZone());
    assertEquals(EXPECTED_CRON_EXPRESSION, actual.getScheduleData().getCron().getCronExpression());
    assertNull(actual.getSchedule());
  }

  @Test
  void testScheduleValidation() throws JsonValidationException {
    final StandardSync actual = new StandardSync();
    assertThrows(JsonValidationException.class, () -> ConnectionScheduleHelper.populateSyncFromScheduleTypeAndData(actual,
        ConnectionScheduleType.CRON, null));
    assertThrows(JsonValidationException.class,
        () -> ConnectionScheduleHelper.populateSyncFromScheduleTypeAndData(actual, ConnectionScheduleType.BASIC, new ConnectionScheduleData()));
    assertThrows(JsonValidationException.class,
        () -> ConnectionScheduleHelper.populateSyncFromScheduleTypeAndData(actual, ConnectionScheduleType.CRON, new ConnectionScheduleData()));
    assertThrows(JsonValidationException.class,
        () -> ConnectionScheduleHelper.populateSyncFromScheduleTypeAndData(actual, ConnectionScheduleType.CRON, new ConnectionScheduleData()
            .cron(new ConnectionScheduleDataCron())));
    assertThrows(JsonValidationException.class,
        () -> ConnectionScheduleHelper.populateSyncFromScheduleTypeAndData(actual, ConnectionScheduleType.CRON, new ConnectionScheduleData()
            .cron(new ConnectionScheduleDataCron().cronExpression(EXPECTED_CRON_EXPRESSION).cronTimeZone("Etc/foo"))));
    assertThrows(JsonValidationException.class,
        () -> ConnectionScheduleHelper.populateSyncFromScheduleTypeAndData(actual, ConnectionScheduleType.CRON, new ConnectionScheduleData()
            .cron(new ConnectionScheduleDataCron().cronExpression("bad cron").cronTimeZone(EXPECTED_CRON_TIMEZONE))));
  }

}
