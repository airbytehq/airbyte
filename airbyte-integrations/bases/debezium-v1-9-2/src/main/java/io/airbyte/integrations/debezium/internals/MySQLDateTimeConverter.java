/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.db.jdbc.DateTimeConverter;
import io.debezium.spi.converter.CustomConverter;
import io.debezium.spi.converter.RelationalColumn;
import java.util.Arrays;
import java.util.Locale;
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

  private final String[] DATE_TYPES = {"DATE", "DATETIME", "TIME", "TIMESTAMP"};

  @Override
  public void configure(final Properties props) {}

  @Override
  public void converterFor(final RelationalColumn field, final ConverterRegistration<SchemaBuilder> registration) {
    if (Arrays.stream(DATE_TYPES).anyMatch(s -> s.equalsIgnoreCase(field.typeName()))) {
      registerDate(field, registration);
    }
  }

  private void registerDate(final RelationalColumn field, final ConverterRegistration<SchemaBuilder> registration) {
    final var fieldType = field.typeName();

    registration.register(SchemaBuilder.string().optional(), x -> {
      if (x == null) {
        return DebeziumConverterUtils.convertDefaultValue(field);
      }

      return switch (fieldType.toUpperCase(Locale.ROOT)) {
        case "DATETIME" -> DateTimeConverter.convertToTimestamp(x);
        case "DATE" -> DateTimeConverter.convertToDate(x);
        case "TIME" -> DateTimeConverter.convertToTime(x);
        case "TIMESTAMP" -> DateTimeConverter.convertToTimestampWithTimezone(x);
        default -> throw new IllegalArgumentException("Unknown field type  " + fieldType.toUpperCase(Locale.ROOT));
      };
    });
  }

}
