/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import java.sql.Date;
import java.sql.SQLException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;
import java.util.function.Function;

/**
 * TODO : Replace all the DateTime related logic of this class with
 * {@link io.airbyte.db.jdbc.DateTimeConverter}
 */
public class DataTypeUtils {

  public static final String DATE_FORMAT_PATTERN = "yyyy-MM-dd'T'HH:mm:ss'Z'";

  public static final String DATE_FORMAT_WITH_MILLISECONDS_PATTERN = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'";

  public static final DateTimeFormatter TIME_FORMATTER = DateTimeFormatter.ofPattern("HH:mm:ss.SSSSSS");
  public static final DateTimeFormatter TIMESTAMP_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSS");
  public static final DateTimeFormatter TIMETZ_FORMATTER = DateTimeFormatter.ofPattern("HH:mm:ss.SSSSSSXXX");
  public static final DateTimeFormatter TIMESTAMPTZ_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.SSSSSSXXX");
  public static final DateTimeFormatter OFFSETDATETIME_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss.SSSSSSS XXX");
  public static final DateTimeFormatter DATE_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd");

  // wrap SimpleDateFormat in a function because SimpleDateFormat is not threadsafe as a static final.
  public static DateFormat getDateFormat() {
    return new SimpleDateFormat(DATE_FORMAT_PATTERN); // Quoted "Z" to indicate UTC, no timezone offset;
  }

  // wrap SimpleDateFormat in a function because SimpleDateFormat is not threadsafe as a static final.
  public static DateFormat getDateFormatMillisPattern() {
    return new SimpleDateFormat(DATE_FORMAT_WITH_MILLISECONDS_PATTERN);
  }

  public static <T> T returnNullIfInvalid(final DataTypeSupplier<T> valueProducer) {
    return returnNullIfInvalid(valueProducer, ignored -> true);
  }

  public static <T> T returnNullIfInvalid(final DataTypeSupplier<T> valueProducer, final Function<T, Boolean> isValidFn) {
    // Some edge case values (e.g: Infinity, NaN) have no java or JSON equivalent, and will throw an
    // exception when parsed. We want to parse those
    // values as null.
    // This method reduces error handling boilerplate.
    try {
      final T value = valueProducer.apply();
      return isValidFn.apply(value) ? value : null;
    } catch (final SQLException e) {
      return null;
    }
  }

  public static String toISO8601StringWithMicroseconds(final Instant instant) {

    final String dateWithMilliseconds = getDateFormatMillisPattern().format(Date.from(instant));
    return dateWithMilliseconds.substring(0, 23) + calculateMicrosecondsString(instant.getNano()) + dateWithMilliseconds.substring(23);
  }

  @SuppressWarnings("PMD.AvoidLiteralsInIfCondition")
  private static String calculateMicrosecondsString(final int nano) {
    final var microSeconds = (nano / 1000) % 1000;
    final String result;
    if (microSeconds < 10) {
      result = "00" + microSeconds;
    } else if (microSeconds < 100) {
      result = "0" + microSeconds;
    } else {
      result = "" + microSeconds;
    }
    return result;
  }

  public static String toISO8601StringWithMilliseconds(final long epochMillis) {
    return getDateFormatMillisPattern().format(Date.from(Instant.ofEpochMilli(epochMillis)));
  }

  public static String toISO8601String(final long epochMillis) {
    return getDateFormat().format(Date.from(Instant.ofEpochMilli(epochMillis)));
  }

  public static String toISO8601String(final java.util.Date date) {
    return getDateFormat().format(date);
  }

  public static String toISOTimeString(final LocalDateTime dateTime) {
    return DateTimeFormatter.ISO_TIME.format(dateTime.toLocalTime());
  }

  public static String toISO8601String(final LocalDate date) {
    return toISO8601String(date.atStartOfDay());
  }

  public static String toISO8601String(final LocalDateTime date) {
    return date.format(DateTimeFormatter.ofPattern(DATE_FORMAT_PATTERN));
  }

  public static String toISO8601String(final OffsetDateTime date) {
    return date.format(OFFSETDATETIME_FORMATTER);
  }

  public static String toISO8601String(final Duration duration) {
    return getDateFormat().format(Date.from(Instant.ofEpochSecond(Math.abs(duration.getSeconds()), Math.abs(duration.getNano()))));
  }

}
