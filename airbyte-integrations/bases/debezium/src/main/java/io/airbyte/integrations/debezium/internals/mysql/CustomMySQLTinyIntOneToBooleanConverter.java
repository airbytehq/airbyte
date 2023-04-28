/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.mysql;

import io.debezium.connector.mysql.converters.TinyIntOneToBooleanConverter;
import io.debezium.spi.converter.RelationalColumn;
import org.apache.kafka.connect.data.SchemaBuilder;

public class CustomMySQLTinyIntOneToBooleanConverter extends TinyIntOneToBooleanConverter {

  @Override
  public void converterFor(final RelationalColumn field, final ConverterRegistration<SchemaBuilder> registration) {
    if (!"TINYINT".equalsIgnoreCase(field.typeName())) {
      return;
    }
    super.converterFor(field, registration);
  }

}
