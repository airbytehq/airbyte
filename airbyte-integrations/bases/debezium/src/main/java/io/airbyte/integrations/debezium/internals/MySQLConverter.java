/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import io.airbyte.db.DataTypeUtils;
import io.debezium.spi.converter.CustomConverter;
import io.debezium.spi.converter.RelationalColumn;
import java.sql.Timestamp;
import java.time.Duration;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeParseException;
import java.util.Arrays;
import java.util.Properties;
import org.apache.kafka.connect.data.SchemaBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This is a custom debezium converter used in MySQL to handle the DATETIME data type. We need a
 * custom converter cause by default debezium returns the DATETIME values as numbers. We need to
 * convert it to proper format. Ref :
 * https://debezium.io/documentation/reference/1.4/development/converters.html This is built from
 * reference with {@link io.debezium.connector.mysql.converters.TinyIntOneToBooleanConverter} If you
 * rename this class then remember to rename the datetime.type property value in
 * {@link io.airbyte-integrations.source.mysql.MySqlCdcProperties#getDebeziumProperties()} (If you
 * don't rename, a test would still fail but it might be tricky to figure out where to change the
 * property name)
 */
public class MySQLConverter implements CustomConverter<SchemaBuilder, RelationalColumn> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySQLConverter.class);

  private final String[] DATE_TYPES = {"DATE", "DATETIME", "TIME"};
  private final String[] TEXT_TYPES = {"VARCHAR", "VARBINARY", "BLOB", "TEXT", "LONGTEXT", "TINYTEXT", "MEDIUMTEXT"};

  @Override
  public void configure(Properties props) {}

  @Override
  public void converterFor(RelationalColumn field, ConverterRegistration<SchemaBuilder> registration) {
    if (Arrays.stream(DATE_TYPES).anyMatch(s -> s.equalsIgnoreCase(field.typeName()))) {
      registerDate(field, registration);
    } else if (Arrays.stream(TEXT_TYPES).anyMatch(s -> s.equalsIgnoreCase(field.typeName()))) {
      registerText(field, registration);
    }
  }

  private void registerText(RelationalColumn field, ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.string(), x -> {
      if (x == null) {
        if (field.isOptional()) {
          return null;
        } else if (field.hasDefaultValue()) {
          return field.defaultValue();
        }
        return null;
      }

      if (x instanceof byte[]) {
        return new String((byte[]) x);
      } else
        return x.toString();
    });
  }

  private void registerDate(RelationalColumn field, ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.string(), x -> {
      if (x == null) {
        if (field.isOptional()) {
          return null;
        } else if (field.hasDefaultValue()) {
          return field.defaultValue();
        }
        return null;
      }
      /**
       * While building this custom converter we were not sure what type debezium could return cause there
       * is no mention of it in the documentation. Secondly if you take a look at
       * {@link io.debezium.connector.mysql.converters.TinyIntOneToBooleanConverter#converterFor(RelationalColumn, ConverterRegistration)}
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
        } catch (DateTimeParseException e) {
          LOGGER.warn("Cannot convert value '{}' to LocalDateTime type", x);
          return x.toString();
        }
      }
      LOGGER.warn("Uncovered date class type '{}'. Use default converter", x.getClass().getName());
      return x.toString();
    });
  }

}
