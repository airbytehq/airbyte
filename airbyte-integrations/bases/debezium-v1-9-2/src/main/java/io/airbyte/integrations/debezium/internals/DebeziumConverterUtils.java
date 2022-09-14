/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import io.airbyte.db.DataTypeUtils;
import io.debezium.spi.converter.RelationalColumn;
import java.sql.Date;
import java.sql.Timestamp;
import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeParseException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class DebeziumConverterUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(DebeziumConverterUtils.class);

  private DebeziumConverterUtils() {
    throw new UnsupportedOperationException();
  }

  /**
   * TODO : Replace usage of this method with {@link io.airbyte.db.jdbc.DateTimeConverter}
   */
  public static String convertDate(final Object input) {
    /**
     * While building this custom converter we were not sure what type debezium could return cause there
     * is no mention of it in the documentation. Secondly if you take a look at
     * {@link io.debezium.connector.mysql.converters.TinyIntOneToBooleanConverter#converterFor(io.debezium.spi.converter.RelationalColumn, io.debezium.spi.converter.CustomConverter.ConverterRegistration)}
     * method, even it is handling multiple data types but its not clear under what circumstances which
     * data type would be returned. I just went ahead and handled the data types that made sense.
     * Secondly, we use LocalDateTime to handle this cause it represents DATETIME datatype in JAVA
     */
    if (input instanceof LocalDateTime) {
      return DataTypeUtils.toISO8601String((LocalDateTime) input);
    } else if (input instanceof LocalDate) {
      return DataTypeUtils.toISO8601String((LocalDate) input);
    } else if (input instanceof Duration) {
      return DataTypeUtils.toISO8601String((Duration) input);
    } else if (input instanceof Timestamp) {
      return DataTypeUtils.toISO8601StringWithMicroseconds((((Timestamp) input).toInstant()));
    } else if (input instanceof Number) {
      return DataTypeUtils.toISO8601String(
          new Timestamp(((Number) input).longValue()).toLocalDateTime());
    } else if (input instanceof Date) {
      return DataTypeUtils.toISO8601String((Date) input);
    } else if (input instanceof String) {
      try {
        return LocalDateTime.parse((String) input).toString();
      } catch (final DateTimeParseException e) {
        LOGGER.warn("Cannot convert value '{}' to LocalDateTime type", input);
        return input.toString();
      }
    }
    LOGGER.warn("Uncovered date class type '{}'. Use default converter", input.getClass().getName());
    return input.toString();
  }

  public static Object convertDefaultValue(final RelationalColumn field) {
    if (field.isOptional()) {
      return null;
    } else if (field.hasDefaultValue()) {
      return field.defaultValue();
    }
    return null;
  }

}
