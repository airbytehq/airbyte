package io.airbyte.integrations.debezium.internals;

import io.debezium.spi.converter.CustomConverter;
import io.debezium.spi.converter.RelationalColumn;
import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.time.format.DateTimeParseException;
import java.util.Properties;
import org.apache.kafka.connect.data.SchemaBuilder;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DateTimeConverter implements CustomConverter<SchemaBuilder, RelationalColumn> {

  private static final String FALLBACK = null;
  private static final Logger LOGGER = LoggerFactory.getLogger(DateTimeConverter.class);

  @Override
  public void configure(Properties props) {

  }

  @Override
  public void converterFor(RelationalColumn field, ConverterRegistration<SchemaBuilder> registration) {
    if (!"DATETIME".equalsIgnoreCase(field.typeName())) {
      return;
    }
    registration.register(SchemaBuilder.string(), x -> {
      if (x == null) {
        if (field.isOptional()) {
          return null;
        } else if (field.hasDefaultValue()) {
          return field.defaultValue();
        }
        return FALLBACK;
      }
      if (x instanceof LocalDateTime) {
        return x.toString();
      } else if (x instanceof Timestamp) {
        return ((Timestamp) x).toLocalDateTime().toString();
      } else if (x instanceof Number) {
        return new Timestamp(((Number) x).intValue()).toLocalDateTime().toString();
      } else if (x instanceof String) {
        try {
          return LocalDateTime.parse((String) x).toString();
        } catch (DateTimeParseException e) {
          return x.toString();
        }
      }
      LOGGER.warn("Cannot convert '{}' to boolean", x.getClass());
      return x.toString();
    });
  }

}
