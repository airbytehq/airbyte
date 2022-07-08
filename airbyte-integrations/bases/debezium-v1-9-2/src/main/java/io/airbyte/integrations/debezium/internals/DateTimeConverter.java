/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import static io.airbyte.db.DataTypeUtils.TIMESTAMPTZ_FORMATTER;
import static io.airbyte.db.DataTypeUtils.TIMESTAMP_FORMATTER;
import static io.airbyte.db.DataTypeUtils.TIMETZ_FORMATTER;
import static io.airbyte.db.DataTypeUtils.TIME_FORMATTER;
import static io.airbyte.db.jdbc.AbstractJdbcCompatibleSourceOperations.isBCE;

import java.sql.Date;
import java.sql.Timestamp;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.OffsetDateTime;
import java.time.OffsetTime;
import java.time.ZoneOffset;
import java.time.format.DateTimeFormatter;

public class DateTimeConverter {

  public static final DateTimeFormatter TIME_WITH_TIMEZONE_FORMATTER = DateTimeFormatter.ofPattern(
      "HH:mm:ss[.][SSSSSSSSS][SSSSSSS][SSSSSS][SSSSS][SSSS][SSS][SS][S][''][XXX][XX][X]");

  public static String convertToTimeWithTimezone(Object time) {
    OffsetTime timetz = OffsetTime.parse(time.toString(), TIME_WITH_TIMEZONE_FORMATTER);
    return timetz.format(TIMETZ_FORMATTER);
  }

  public static String convertToTimestampWithTimezone(Object timestamp) {
    OffsetDateTime timestamptz = OffsetDateTime.ofInstant(toInstant(timestamp), ZoneOffset.UTC);
    LocalDate localDate = timestamptz.toLocalDate();
    return resolveEra(localDate, timestamptz.format(TIMESTAMPTZ_FORMATTER));
  }

  public static String convertToTimestamp(Object timestamp) {
    final LocalDateTime localDateTime = LocalDateTime.ofInstant(toInstant(timestamp),
        ZoneOffset.UTC);
    final LocalDate date = localDateTime.toLocalDate();
    return resolveEra(date, localDateTime.format(TIMESTAMP_FORMATTER));
  }

  public static Object convertToDate(Object date) {
    LocalDate localDate;
    if (date instanceof Date) {
      localDate = ((Date) date).toLocalDate();
    } else {
      localDate = LocalDate.parse(date.toString());
    }
    return resolveEra(localDate, localDate.toString());
  }

  public static String convertToTime(Object time) {
    LocalTime localTime = LocalTime.parse(time.toString());
    return localTime.format(TIME_FORMATTER);
  }

  public static String resolveEra(LocalDate date, String value) {
    return isBCE(date) ? value.substring(1) + " BC" : value;
  }

  private static Instant toInstant(Object timestamp) {
    if (timestamp instanceof Timestamp) {
      return ((Timestamp) timestamp).toInstant();
    } else {
      return Instant.parse(timestamp.toString());
    }
  }

}
