/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs.migrations;

import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.Test;

public class CronScheduleMigrationTest {

  @Test
  public void testDefaultSchedule() {
    // default is daily 0 0 */1 * *
    Assertions.assertEquals("0 0 */1 * *", V0_29_21_001__change_schedule_to_string.cronFor(Jsons.emptyObject()));
    Assertions.assertEquals("0 0 */1 * *", V0_29_21_001__change_schedule_to_string.cronFor("unknown", 0));
  }

  @Test
  public void testMostCommonSchedulesSetFromUi() {
    // UI only allows few schedules.
    // 5,10,15,30 minutes
    // 1,2,3,6,8,12,24 hours
    Assertions.assertEquals("*/5 * * * *", V0_29_21_001__change_schedule_to_string.cronFor("minutes", 5));
    Assertions.assertEquals("*/10 * * * *", V0_29_21_001__change_schedule_to_string.cronFor("minutes", 10));
    Assertions.assertEquals("*/15 * * * *", V0_29_21_001__change_schedule_to_string.cronFor("minutes", 15));
    Assertions.assertEquals("*/30 * * * *", V0_29_21_001__change_schedule_to_string.cronFor("minutes", 30));

    Assertions.assertEquals("0 */1 * * *", V0_29_21_001__change_schedule_to_string.cronFor("hours", 1));
    Assertions.assertEquals("0 */2 * * *", V0_29_21_001__change_schedule_to_string.cronFor("hours", 2));
    Assertions.assertEquals("0 */3 * * *", V0_29_21_001__change_schedule_to_string.cronFor("hours", 3));
    Assertions.assertEquals("0 */6 * * *", V0_29_21_001__change_schedule_to_string.cronFor("hours", 6));
    Assertions.assertEquals("0 */8 * * *", V0_29_21_001__change_schedule_to_string.cronFor("hours", 8));
    Assertions.assertEquals("0 */12 * * *", V0_29_21_001__change_schedule_to_string.cronFor("hours", 12));
    Assertions.assertEquals("0 0 */1 * *", V0_29_21_001__change_schedule_to_string.cronFor("hours", 24));
  }

  @Test
  public void testOtherCommonSchedulesSetFromApiNotAvailableFromUi() {
    // days, weeks and months
    Assertions.assertEquals("0 0 */2 * *", V0_29_21_001__change_schedule_to_string.cronFor("days", 2));
    Assertions.assertEquals("0 0 */7 * *", V0_29_21_001__change_schedule_to_string.cronFor("days", 7));
    Assertions.assertEquals("0 0 */15 * *", V0_29_21_001__change_schedule_to_string.cronFor("days", 15));

    Assertions.assertEquals("0 0 */7 * *", V0_29_21_001__change_schedule_to_string.cronFor("weeks", 1));
    Assertions.assertEquals("0 0 */14 * *", V0_29_21_001__change_schedule_to_string.cronFor("weeks", 2));
    Assertions.assertEquals("0 0 */21 * *", V0_29_21_001__change_schedule_to_string.cronFor("weeks", 3));

    Assertions.assertEquals("0 0 * */1 *", V0_29_21_001__change_schedule_to_string.cronFor("months", 1));
    Assertions.assertEquals("0 0 * */3 *", V0_29_21_001__change_schedule_to_string.cronFor("months", 3));
    Assertions.assertEquals("0 0 * */6 *", V0_29_21_001__change_schedule_to_string.cronFor("months", 6));
  }

  @Test
  public void testMinuteSchedulesThatGetsConvertedToHigherTimeUnits() {
    // these are approximate, rounded up
    Assertions.assertEquals("0 */1 * * *", V0_29_21_001__change_schedule_to_string.cronFor("minutes", 75));
    Assertions.assertEquals("0 */2 * * *", V0_29_21_001__change_schedule_to_string.cronFor("minutes", 100));
    Assertions.assertEquals("0 */12 * * *", V0_29_21_001__change_schedule_to_string.cronFor("minutes", 720));
    Assertions.assertEquals("0 0 */1 * *", V0_29_21_001__change_schedule_to_string.cronFor("minutes", 1440));
    Assertions.assertEquals("0 0 */1 * *", V0_29_21_001__change_schedule_to_string.cronFor("minutes", 2000));
    Assertions.assertEquals("0 0 */2 * *", V0_29_21_001__change_schedule_to_string.cronFor("minutes", 3000));
    Assertions.assertEquals("0 0 * */12 *", V0_29_21_001__change_schedule_to_string.cronFor("minutes", 535680));
    Assertions.assertEquals("0 0 * */12 *", V0_29_21_001__change_schedule_to_string.cronFor("minutes", 555000));
  }

  @Test
  public void testHourSchedulesThatGetsConvertedToHigherTimeUnits() {
    // these are approximate, rounded up
    Assertions.assertEquals("0 0 */1 * *", V0_29_21_001__change_schedule_to_string.cronFor("hours", 25));
    Assertions.assertEquals("0 0 */1 * *", V0_29_21_001__change_schedule_to_string.cronFor("hours", 35));
    Assertions.assertEquals("0 0 */2 * *", V0_29_21_001__change_schedule_to_string.cronFor("hours", 38));
    Assertions.assertEquals("0 0 */21 * *", V0_29_21_001__change_schedule_to_string.cronFor("hours", 500));
    Assertions.assertEquals("0 0 * */1 *", V0_29_21_001__change_schedule_to_string.cronFor("hours", 760));
    Assertions.assertEquals("0 0 * */6 *", V0_29_21_001__change_schedule_to_string.cronFor("hours", 4500));
    Assertions.assertEquals("0 0 * */12 *", V0_29_21_001__change_schedule_to_string.cronFor("hours", 9000));
    Assertions.assertEquals("0 0 * */12 *", V0_29_21_001__change_schedule_to_string.cronFor("hours", 15000));
  }

  @Test
  public void testDaySchedulesThatGetsConvertedToHigherTimeUnits() {
    // these are approximate, rounded up
    Assertions.assertEquals("0 0 * */1 *", V0_29_21_001__change_schedule_to_string.cronFor("days", 31));
    Assertions.assertEquals("0 0 * */3 *", V0_29_21_001__change_schedule_to_string.cronFor("days", 100));
    Assertions.assertEquals("0 0 * */4 *", V0_29_21_001__change_schedule_to_string.cronFor("days", 105));
    Assertions.assertEquals("0 0 * */12 *", V0_29_21_001__change_schedule_to_string.cronFor("days", 365));
    Assertions.assertEquals("0 0 * */12 *", V0_29_21_001__change_schedule_to_string.cronFor("days", 1000));
  }

  @Test
  public void testMonthSchedulesCapsAtTwelveMonths() {
    Assertions.assertEquals("0 0 * */1 *", V0_29_21_001__change_schedule_to_string.cronFor("months", 1));
    Assertions.assertEquals("0 0 * */7 *", V0_29_21_001__change_schedule_to_string.cronFor("months", 7));
    Assertions.assertEquals("0 0 * */12 *", V0_29_21_001__change_schedule_to_string.cronFor("months", 12));
    Assertions.assertEquals("0 0 * */12 *", V0_29_21_001__change_schedule_to_string.cronFor("months", 15));
    Assertions.assertEquals("0 0 * */12 *", V0_29_21_001__change_schedule_to_string.cronFor("months", 100));
  }

}
