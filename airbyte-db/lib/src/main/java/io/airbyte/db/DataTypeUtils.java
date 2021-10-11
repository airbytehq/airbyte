/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import java.sql.Date;
import java.sql.SQLException;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.time.Instant;
import java.util.function.Function;

public class DataTypeUtils {

  public static final DateFormat DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'"); // Quoted "Z" to indicate UTC, no timezone offset

  public static <T> T returnNullIfInvalid(DataTypeSupplier<T> valueProducer) {
    return returnNullIfInvalid(valueProducer, ignored -> true);
  }

  public static <T> T returnNullIfInvalid(DataTypeSupplier<T> valueProducer, Function<T, Boolean> isValidFn) {
    // Some edge case values (e.g: Infinity, NaN) have no java or JSON equivalent, and will throw an
    // exception when parsed. We want to parse those
    // values as null.
    // This method reduces error handling boilerplate.
    try {
      T value = valueProducer.apply();
      return isValidFn.apply(value) ? value : null;
    } catch (SQLException e) {
      return null;
    }
  }

  public static String toISO8601String(long epochMillis) {
    return DATE_FORMAT.format(Date.from(Instant.ofEpochMilli(epochMillis)));
  }

  public static String toISO8601String(java.util.Date date) {
    return DATE_FORMAT.format(date);
  }

}
