/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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
import java.time.format.DateTimeFormatter;
import java.util.function.Function;

public class DataTypeUtils {

  public static final String DATE_FORMAT_PATTERN = "yyyy-MM-dd'T'HH:mm:ss'Z'";
  public static final DateFormat DATE_FORMAT = new SimpleDateFormat(DATE_FORMAT_PATTERN); // Quoted "Z" to indicate UTC, no timezone offset

  public static final String DATE_FORMAT_WITH_MILLISECONDS_PATTERN = "yyyy-MM-dd'T'HH:mm:ss.SSS'Z'";
  public static final DateFormat DATE_FORMAT_WITH_MILLISECONDS = new SimpleDateFormat(DATE_FORMAT_WITH_MILLISECONDS_PATTERN);

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

  public static String toISO8601StringWithMilliseconds(final long epochMillis) {
    return DATE_FORMAT_WITH_MILLISECONDS.format(Date.from(Instant.ofEpochMilli(epochMillis)));
  }

  public static String toISO8601String(final long epochMillis) {
    return DATE_FORMAT.format(Date.from(Instant.ofEpochMilli(epochMillis)));
  }

  public static String toISO8601String(final java.util.Date date) {
    return DATE_FORMAT.format(date);
  }

  public static String toISO8601String(final LocalDate date) {
    return toISO8601String(date.atStartOfDay());
  }

  public static String toISO8601String(final LocalDateTime date) {
    return date.format(DateTimeFormatter.ofPattern(DATE_FORMAT_PATTERN));
  }

  public static String toISO8601String(final Duration duration) {
    return DATE_FORMAT.format(Date.from(Instant.ofEpochSecond(Math.abs(duration.getSeconds()), Math.abs(duration.getNano()))));
  }

}
