/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import static io.airbyte.db.DataTypeUtils.TIMESTAMPTZ_FORMATTER;
import static io.airbyte.db.DataTypeUtils.TIMESTAMP_FORMATTER;
import static io.airbyte.db.DataTypeUtils.TIMETZ_FORMATTER;
import static io.airbyte.db.DataTypeUtils.TIME_FORMATTER;
import static io.airbyte.db.jdbc.AbstractJdbcCompatibleSourceOperations.resolveEra;

import java.sql.Date;
import java.sql.Timestamp;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.OffsetDateTime;
import java.time.OffsetTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;

public class DateTimeConverter {

  public static final DateTimeFormatter TIME_WITH_TIMEZONE_FORMATTER = DateTimeFormatter.ofPattern(
      "HH:mm:ss[.][SSSSSSSSS][SSSSSSS][SSSSSS][SSSSS][SSSS][SSS][SS][S][''][XXX][XX][X]");

  public static String convertToTimeWithTimezone(Object time) {
    OffsetTime timetz = OffsetTime.parse(time.toString(), TIME_WITH_TIMEZONE_FORMATTER);
    return timetz.format(TIMETZ_FORMATTER);
  }

  public static String convertToTimestampWithTimezone(Object timestamp) {
    if (timestamp instanceof Timestamp t) {
      // Conceptually, a timestamp with timezone is an Instant. But t.toInstant() actually mangles the value for ancient dates,
      // because leap years weren't applied consistently in ye olden days.
      // Additionally, toInstant() (and toLocalDateTime()) actually lose the era indicator, so we can't rely on their getEra() methods.
      // So we have special handling for this case, which sidesteps the toInstant conversion.
      ZonedDateTime timestamptz = t.toLocalDateTime().atZone(ZoneOffset.UTC);
      String value = timestamptz.format(TIMESTAMPTZ_FORMATTER);
      return resolveEra(t, value);
    } else {
      Instant instant = Instant.parse(timestamp.toString());
      OffsetDateTime offsetDateTime = OffsetDateTime.ofInstant(instant, ZoneOffset.UTC);
      ZonedDateTime timestamptz = ZonedDateTime.from(offsetDateTime);
      LocalDate localDate = timestamptz.toLocalDate();
      String value = timestamptz.format(TIMESTAMPTZ_FORMATTER);
      return resolveEra(localDate, value);
    }
  }

  /**
   * See {@link #convertToTimestampWithTimezone(Object)} for explanation.
   */
  public static String convertToTimestamp(Object timestamp) {
    if (timestamp instanceof Timestamp t) {
      LocalDateTime localDateTime = t.toLocalDateTime();
      String value = localDateTime.format(TIMESTAMP_FORMATTER);
      return resolveEra(t, value);
    } else {
      LocalDateTime localDateTime = LocalDateTime.parse(timestamp.toString());
      final LocalDate date = localDateTime.toLocalDate();
      String value = localDateTime.format(TIMESTAMP_FORMATTER);
      return resolveEra(date, value);
    }
  }

  public static Object convertToDate(Object date) {
    if (date instanceof Date d) {
      LocalDate localDate = ((Date) date).toLocalDate();
      return resolveEra(d, localDate.toString());
    } else {
      LocalDate localDate = LocalDate.parse(date.toString());
      return resolveEra(localDate, localDate.toString());
    }
  }

  public static String convertToTime(Object time) {
    LocalTime localTime = LocalTime.parse(time.toString());
    return localTime.format(TIME_FORMATTER);
  }
}
