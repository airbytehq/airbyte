/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.jdbc;

import static io.airbyte.db.DataTypeUtils.DATE_FORMATTER;
import static io.airbyte.db.DataTypeUtils.TIMESTAMPTZ_FORMATTER;
import static io.airbyte.db.DataTypeUtils.TIMESTAMP_FORMATTER;
import static io.airbyte.db.DataTypeUtils.TIMETZ_FORMATTER;
import static io.airbyte.db.DataTypeUtils.TIME_FORMATTER;
import static io.airbyte.db.jdbc.AbstractJdbcCompatibleSourceOperations.resolveEra;
import static java.time.ZoneOffset.UTC;

import com.fasterxml.jackson.databind.node.ObjectNode;
import java.sql.Date;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Time;
import java.sql.Timestamp;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.OffsetDateTime;
import java.time.OffsetTime;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.TimeUnit;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DateTimeConverter {

  private static final Logger LOGGER = LoggerFactory.getLogger(DateTimeConverter.class);
  public static final DateTimeFormatter TIME_WITH_TIMEZONE_FORMATTER = DateTimeFormatter.ofPattern(
      "HH:mm:ss[.][SSSSSSSSS][SSSSSSS][SSSSSS][SSSSS][SSSS][SSS][SS][S][''][XXX][XX][X]");
  private static boolean loggedUnknownTimeWithTimeZoneClass = false;
  private static boolean loggedUnknownTimeClass = false;
  private static boolean loggedUnknownTimestampWithTimeZoneClass = false;
  private static boolean loggedUnknownTimestampClass = false;
  private static boolean loggedUnknownDateClass = false;

  public static String convertToTimeWithTimezone(final Object time) {
    if (time instanceof final java.time.OffsetTime timetz) {
      return timetz.format(TIMETZ_FORMATTER);
    } else {
      if (!loggedUnknownTimeWithTimeZoneClass) {
        LOGGER.info("Unknown class for Time with timezone data type" + time.getClass());
        loggedUnknownTimeWithTimeZoneClass = true;
      }
      final OffsetTime timetz = OffsetTime.parse(time.toString(), TIME_WITH_TIMEZONE_FORMATTER);
      return timetz.format(TIMETZ_FORMATTER);
    }
  }

  public static String convertToTimestampWithTimezone(final Object timestamp) {
    if (timestamp instanceof final Timestamp t) {
      // In snapshot mode, debezium produces a java.sql.Timestamp object for the TIMESTAMPTZ type.
      // Conceptually, a timestamp with timezone is an Instant. But t.toInstant() actually mangles the
      // value for ancient dates, because leap years weren't applied consistently in ye olden days.
      // Additionally, toInstant() (and toLocalDateTime()) actually lose the era indicator, so we can't
      // rely on their getEra() methods.
      // So we have special handling for this case, which sidesteps the toInstant conversion.
      final ZonedDateTime timestamptz = t.toLocalDateTime().atZone(UTC);
      final String value = timestamptz.format(TIMESTAMPTZ_FORMATTER);
      return resolveEra(t, value);
    } else if (timestamp instanceof final OffsetDateTime t) {
      return resolveEra(t.toLocalDate(), t.format(TIMESTAMPTZ_FORMATTER));
    } else if (timestamp instanceof final ZonedDateTime timestamptz) {
      return resolveEra(timestamptz.toLocalDate(), timestamptz.format(TIMESTAMPTZ_FORMATTER));
    } else if (timestamp instanceof final Instant instant) {
      final OffsetDateTime offsetDateTime = OffsetDateTime.ofInstant(instant, UTC);
      final ZonedDateTime timestamptz = ZonedDateTime.from(offsetDateTime);
      final LocalDate localDate = timestamptz.toLocalDate();
      final String value = timestamptz.format(TIMESTAMPTZ_FORMATTER);
      return resolveEra(localDate, value);
    } else {
      if (!loggedUnknownTimestampWithTimeZoneClass) {
        LOGGER.info("Unknown class for Timestamp with time zone data type" + timestamp.getClass());
        loggedUnknownTimestampWithTimeZoneClass = true;
      }
      final Instant instant = Instant.parse(timestamp.toString());
      final OffsetDateTime offsetDateTime = OffsetDateTime.ofInstant(instant, UTC);
      final ZonedDateTime timestamptz = ZonedDateTime.from(offsetDateTime);
      final LocalDate localDate = timestamptz.toLocalDate();
      final String value = timestamptz.format(TIMESTAMPTZ_FORMATTER);
      return resolveEra(localDate, value);
    }
  }

  /**
   * See {@link #convertToTimestampWithTimezone(Object)} for explanation of the weird things happening
   * here.
   */
  public static String convertToTimestamp(final Object timestamp) {
    if (timestamp instanceof final Timestamp t) {
      // Snapshot mode
      final LocalDateTime localDateTime = t.toLocalDateTime();
      final String value = localDateTime.format(TIMESTAMP_FORMATTER);
      return resolveEra(t, value);
    } else if (timestamp instanceof final Instant i) {
      // Incremental mode
      return resolveEra(i.atZone(UTC).toLocalDate(), i.atOffset(UTC).toLocalDateTime().format(TIMESTAMP_FORMATTER));
    } else if (timestamp instanceof final LocalDateTime localDateTime) {
      final LocalDate date = localDateTime.toLocalDate();
      final String value = localDateTime.format(TIMESTAMP_FORMATTER);
      return resolveEra(date, value);
    } else {
      if (!loggedUnknownTimestampClass) {
        LOGGER.info("Unknown class for Timestamp data type" + timestamp.getClass());
        loggedUnknownTimestampClass = true;
      }
      final LocalDateTime localDateTime = LocalDateTime.parse(timestamp.toString());
      final LocalDate date = localDateTime.toLocalDate();
      final String value = localDateTime.format(TIMESTAMP_FORMATTER);
      return resolveEra(date, value);
    }
  }

  /**
   * See {@link #convertToTimestampWithTimezone(Object)} for explanation of the weird things happening
   * here.
   */
  public static String convertToDate(final Object date) {
    if (date instanceof final Date d) {
      // Snapshot mode
      final LocalDate localDate = ((Date) date).toLocalDate();
      return resolveEra(d, localDate.format(DATE_FORMATTER));
    } else if (date instanceof LocalDate d) {
      // Incremental mode
      return resolveEra(d, d.format(DATE_FORMATTER));
    } else {
      if (!loggedUnknownDateClass) {
        LOGGER.info("Unknown class for Date data type" + date.getClass());
        loggedUnknownDateClass = true;
      }
      final LocalDate localDate = LocalDate.parse(date.toString());
      return resolveEra(localDate, localDate.format(DATE_FORMATTER));
    }
  }

  public static String convertToTime(final Object time) {
    if (time instanceof final Time sqlTime) {
      return sqlTime.toLocalTime().format(TIME_FORMATTER);
    } else if (time instanceof final LocalTime localTime) {
      return localTime.format(TIME_FORMATTER);
    } else if (time instanceof java.time.Duration) {
      long value = ((Duration) time).toNanos();
      if (value >= 0 && value < TimeUnit.DAYS.toNanos(1)) {
        return LocalTime.ofNanoOfDay(value).format(TIME_FORMATTER);
      } else {
        final long updatedValue = Math.min(Math.abs(value), LocalTime.MAX.toNanoOfDay());
        LOGGER.debug("Time values must use number of nanoseconds greater than 0 and less than 86400000000000 but its {}, converting to {} ", value,
            updatedValue);
        return LocalTime.ofNanoOfDay(updatedValue).format(TIME_FORMATTER);
      }
    } else {
      if (!loggedUnknownTimeClass) {
        LOGGER.info("Unknown class for Time data type" + time.getClass());
        loggedUnknownTimeClass = true;
      }

      final String valueAsString = time.toString();
      if (valueAsString.startsWith("24")) {
        LOGGER.debug("Time value {} is above range, converting to 23:59:59", valueAsString);
        return LocalTime.MAX.format(TIME_FORMATTER);
      }
      return LocalTime.parse(valueAsString).format(TIME_FORMATTER);
    }
  }

  public static void putJavaSQLDate(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    final Date date = resultSet.getDate(index);
    node.put(columnName, convertToDate(date));
  }

  public static void putJavaSQLTime(ObjectNode node, String columnName, ResultSet resultSet, int index) throws SQLException {
    // resultSet.getTime() will lose nanoseconds precision
    final LocalTime localTime = resultSet.getTimestamp(index).toLocalDateTime().toLocalTime();
    node.put(columnName, convertToTime(localTime));
  }

}
