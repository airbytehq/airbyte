/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.microsoft.sqlserver.jdbc.Geography;
import com.microsoft.sqlserver.jdbc.Geometry;
import com.microsoft.sqlserver.jdbc.SQLServerException;
import io.airbyte.db.DataTypeUtils;
import io.debezium.spi.converter.CustomConverter;
import io.debezium.spi.converter.RelationalColumn;
import java.math.BigDecimal;
import java.nio.charset.Charset;
import java.sql.Timestamp;
import java.time.OffsetDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Objects;
import java.util.Properties;
import java.util.Set;
import microsoft.sql.DateTimeOffset;
import org.apache.kafka.connect.data.SchemaBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MSSQLConverter implements CustomConverter<SchemaBuilder, RelationalColumn> {

  private final Logger LOGGER = LoggerFactory.getLogger(MSSQLConverter.class);

  private final Set<String> DATE_TYPES = Set.of("DATE", "DATETIME", "DATETIME2", "SMALLDATETIME");
  private final Set<String> BINARY = Set.of("VARBINARY", "BINARY");
  private static final String DATETIMEOFFSET = "DATETIMEOFFSET";
  private static final String TIME_TYPE = "TIME";
  private static final String SMALLMONEY_TYPE = "SMALLMONEY";
  private static final String GEOMETRY = "GEOMETRY";
  private static final String GEOGRAPHY = "GEOGRAPHY";
  private static final String DEBEZIUM_DATETIMEOFFSET_FORMAT = "yyyy-MM-dd HH:mm:ss XXX";

  @Override
  public void configure(Properties props) {}

  @Override
  public void converterFor(final RelationalColumn field,
                           final ConverterRegistration<SchemaBuilder> registration) {
    if (DATE_TYPES.contains(field.typeName().toUpperCase())) {
      registerDate(field, registration);
    } else if (SMALLMONEY_TYPE.equalsIgnoreCase(field.typeName())) {
      registerMoney(field, registration);
    } else if (BINARY.contains(field.typeName().toUpperCase())) {
      registerBinary(field, registration);
    } else if (GEOMETRY.equalsIgnoreCase(field.typeName())) {
      registerGeometry(field, registration);
    } else if (GEOGRAPHY.equalsIgnoreCase(field.typeName())) {
      registerGeography(field, registration);
    } else if (TIME_TYPE.equalsIgnoreCase(field.typeName())) {
      registerTime(field, registration);
    } else if (DATETIMEOFFSET.equalsIgnoreCase(field.typeName())) {
      registerDateTimeOffSet(field, registration);
    }
  }

  private void registerGeometry(final RelationalColumn field,
                                final ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.string(), input -> {
      if (Objects.isNull(input)) {
        return DebeziumConverterUtils.convertDefaultValue(field);
      }

      if (input instanceof byte[]) {
        try {
          return Geometry.deserialize((byte[]) input).toString();
        } catch (SQLServerException e) {
          LOGGER.error(e.getMessage());
        }
      }

      LOGGER.warn("Uncovered Geometry class type '{}'. Use default converter",
          input.getClass().getName());
      return input.toString();
    });
  }

  private void registerGeography(final RelationalColumn field,
                                 final ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.string(), input -> {
      if (Objects.isNull(input)) {
        return DebeziumConverterUtils.convertDefaultValue(field);
      }

      if (input instanceof byte[]) {
        try {
          return Geography.deserialize((byte[]) input).toString();
        } catch (SQLServerException e) {
          LOGGER.error(e.getMessage());
        }
      }

      LOGGER.warn("Uncovered Geography class type '{}'. Use default converter",
          input.getClass().getName());
      return input.toString();
    });
  }

  private void registerDate(final RelationalColumn field,
                            final ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.string(), input -> {
      if (Objects.isNull(input)) {
        return DebeziumConverterUtils.convertDefaultValue(field);
      }

      return DebeziumConverterUtils.convertDate(input);
    });
  }

  private void registerDateTimeOffSet(final RelationalColumn field,
                                      final ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.string(), input -> {
      if (Objects.isNull(input)) {
        return DebeziumConverterUtils.convertDefaultValue(field);
      }

      if (input instanceof DateTimeOffset) {
        return DataTypeUtils.toISO8601String(
            OffsetDateTime.parse(input.toString(),
                DateTimeFormatter.ofPattern(DEBEZIUM_DATETIMEOFFSET_FORMAT)));
      }

      LOGGER.warn("Uncovered DateTimeOffSet class type '{}'. Use default converter",
          input.getClass().getName());
      return input.toString();
    });
  }

  private void registerTime(final RelationalColumn field,
                            final ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.string(), input -> {
      if (Objects.isNull(input)) {
        return DebeziumConverterUtils.convertDefaultValue(field);
      }

      if (input instanceof Timestamp) {
        return DataTypeUtils.toISOTimeString(((Timestamp) input).toLocalDateTime());
      }

      LOGGER.warn("Uncovered time class type '{}'. Use default converter",
          input.getClass().getName());
      return input.toString();
    });
  }

  private void registerMoney(final RelationalColumn field,
                             final ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.float64(), input -> {
      if (Objects.isNull(input)) {
        return DebeziumConverterUtils.convertDefaultValue(field);
      }

      if (input instanceof BigDecimal) {
        return ((BigDecimal) input).doubleValue();
      }

      LOGGER.warn("Uncovered money class type '{}'. Use default converter",
          input.getClass().getName());
      return input.toString();
    });
  }

  private void registerBinary(final RelationalColumn field,
                              final ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.string(), input -> {
      if (Objects.isNull(input)) {
        return DebeziumConverterUtils.convertDefaultValue(field);
      }

      if (input instanceof byte[]) {
        return new String((byte[]) input, Charset.defaultCharset());
      }

      LOGGER.warn("Uncovered binary class type '{}'. Use default converter",
          input.getClass().getName());
      return input.toString();
    });
  }

}
