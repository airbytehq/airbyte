/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import io.airbyte.db.DataTypeUtils;
import io.debezium.spi.converter.CustomConverter;
import io.debezium.spi.converter.RelationalColumn;
import java.math.BigDecimal;
import java.sql.Timestamp;
import java.time.format.DateTimeFormatter;
import java.util.Objects;
import java.util.Properties;
import org.apache.kafka.connect.data.SchemaBuilder;
import org.apache.kafka.connect.data.Time;
import org.apache.logging.log4j.core.config.plugins.convert.DateTypeConverter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MSSQLConverter implements CustomConverter<SchemaBuilder, RelationalColumn> {

  private final Logger LOGGER = LoggerFactory.getLogger(MSSQLConverter.class);

  private final String DATE_TYPE = "DATE";
  private final String DATETIME_TYPE = "DATETIME";
  private final String DATETIME2_TYPE = "DATETIME2";
  private final String DATETIMEOFFSET = "DATETIMEOFFSET";
  private final String TIME_TYPE = "TIME";
  private final String SMALLDATETIME_TYPE = "SMALLDATETIME";
  private final String SMALLMONEY_TYPE = "SMALLMONEY";

  @Override
  public void configure(Properties props) {
  }

  @Override
  public void converterFor(final RelationalColumn field,
      final ConverterRegistration<SchemaBuilder> registration) {
    if (DATE_TYPE.equalsIgnoreCase(field.typeName())
        || DATETIME_TYPE.equalsIgnoreCase(field.typeName())
        || DATETIME2_TYPE.equalsIgnoreCase(field.typeName())
        || DATETIMEOFFSET.equalsIgnoreCase(field.typeName())
        || SMALLDATETIME_TYPE.equalsIgnoreCase(field.typeName())) {
      registerDate(field, registration);
    } else if (SMALLMONEY_TYPE.equalsIgnoreCase(field.typeName())) {
      registerMoney(field, registration);
    } else if (TIME_TYPE.equalsIgnoreCase(field.typeName())) {
      registerTime(field, registration);
    }
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

}
