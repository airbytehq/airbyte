/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import io.debezium.spi.converter.CustomConverter;
import io.debezium.spi.converter.RelationalColumn;
import java.util.Objects;
import java.util.Properties;
import org.apache.kafka.connect.data.SchemaBuilder;

public class MSSQLConverter implements CustomConverter<SchemaBuilder, RelationalColumn> {

  private final String SMALLDATETIME_TYPE = "SMALLDATETIME";
  private final String SMALLMONEY_TYPE = "SMALLMONEY";

  @Override
  public void configure(Properties props) {}

  @Override
  public void converterFor(final RelationalColumn field,
                           final ConverterRegistration<SchemaBuilder> registration) {
    if (SMALLDATETIME_TYPE.equalsIgnoreCase(field.typeName())) {
      registerDate(field, registration);
    } else if (SMALLMONEY_TYPE.equalsIgnoreCase(field.typeName())) {
      registerMoney(field, registration);
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

  private void registerMoney(final RelationalColumn field,
                             final ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.float64(), input -> {
      if (Objects.isNull(input)) {
        return DebeziumConverterUtils.convertDefaultValue(field);
      }

      return DebeziumConverterUtils.convertMoney(input);
    });

  }

}
