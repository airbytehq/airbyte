/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.DataTypeUtils;
import io.debezium.spi.converter.CustomConverter;
import io.debezium.spi.converter.RelationalColumn;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.Properties;
import org.apache.kafka.connect.data.SchemaBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This is a custom debezium converter used in MySQL to handle the DATETIME data type. We need a
 * custom converter cause by default debezium returns the DATETIME values as numbers. We need to
 * convert it to proper format. Ref :
 * https://debezium.io/documentation/reference/1.9/development/converters.html This is built from
 * reference with {@link io.debezium.connector.mysql.converters.TinyIntOneToBooleanConverter} If you
 * rename this class then remember to rename the datetime.type property value in
 * {@link io.airbyte.integrations.source.mysql.MySqlCdcProperties#getDebeziumProperties(JsonNode)}
 * (If you don't rename, a test would still fail but it might be tricky to figure out where to
 * change the property name)
 */
public class MySQLDateTimeConverter implements CustomConverter<SchemaBuilder, RelationalColumn> {

  private static final Logger LOGGER = LoggerFactory.getLogger(MySQLDateTimeConverter.class);

  private final String[] DATE_TYPES = {"DATE", "DATETIME", "TIME"};

  @Override
  public void configure(final Properties props) {}

  @Override
  public void converterFor(final RelationalColumn field, final ConverterRegistration<SchemaBuilder> registration) {
    if (Arrays.stream(DATE_TYPES).anyMatch(s -> s.equalsIgnoreCase(field.typeName()))) {
      registerDate(field, registration);
    }
  }

  /**
   * The debezium driver replaces Zero-value by Null even when this column is mandatory. According to
   * the doc, it should be done by driver, but it fails.
   */
  private Object convertDefaultValueNullDate(final RelationalColumn field) {
    final var defaultValue = DebeziumConverterUtils.convertDefaultValue(field);
    return (defaultValue == null && !field.isOptional() ? DataTypeUtils.toISO8601String(LocalDate.EPOCH) : defaultValue);
  }

  private void registerDate(final RelationalColumn field, final ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.string(),
        x -> x == null ? convertDefaultValueNullDate(field) : DebeziumConverterUtils.convertDate(x));
  }

}
