package io.airbyte.integrations.debezium.internals;

import io.airbyte.db.DataTypeUtils;
import io.debezium.spi.converter.RelationalColumn;
import java.sql.Timestamp;
import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeParseException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DebeziumConverterUtils {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresConverter.class);

  public static String convertDate(Object x) {
    /**
     * While building this custom converter we were not sure what type debezium could return cause there
     * is no mention of it in the documentation. Secondly if you take a look at
     * {@link io.debezium.connector.mysql.converters.TinyIntOneToBooleanConverter#converterFor(io.debezium.spi.converter.RelationalColumn, io.debezium.spi.converter.CustomConverter.ConverterRegistration)}
     * method, even it is handling multiple data types but its not clear under what circumstances which
     * data type would be returned. I just went ahead and handled the data types that made sense.
     * Secondly, we use LocalDateTime to handle this cause it represents DATETIME datatype in JAVA
     */
    if (x instanceof LocalDateTime) {
      return DataTypeUtils.toISO8601String((LocalDateTime) x);
    } else if (x instanceof LocalDate) {
      return DataTypeUtils.toISO8601String((LocalDate) x);
    } else if (x instanceof Duration) {
      return DataTypeUtils.toISO8601String((Duration) x);
    } else if (x instanceof Timestamp) {
      return DataTypeUtils.toISO8601String(((Timestamp) x).toLocalDateTime());
    } else if (x instanceof Number) {
      return DataTypeUtils.toISO8601String(new Timestamp(((Number) x).longValue()).toLocalDateTime());
    } else if (x instanceof String) {
      try {
        return LocalDateTime.parse((String) x).toString();
      } catch (final DateTimeParseException e) {
        LOGGER.warn("Cannot convert value '{}' to LocalDateTime type", x);
        return x.toString();
      }
    }
    LOGGER.warn("Uncovered date class type '{}'. Use default converter", x.getClass().getName());
    return x.toString();
  }

  public static Object getDefaultValue(RelationalColumn field) {
    if (field.isOptional()) {
      return null;
    } else if (field.hasDefaultValue()) {
      return field.defaultValue();
    }
    return null;
  }
}
