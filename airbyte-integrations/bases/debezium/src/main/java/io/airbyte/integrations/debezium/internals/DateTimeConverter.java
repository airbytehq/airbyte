/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

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

  private static final Logger LOGGER = LoggerFactory.getLogger(DateTimeConverter.class);

  @Override
  public void configure(Properties props) {}

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
        return null;
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
          LOGGER.warn("Cannot convert value '{}' to LocalDateTime type", x);
          return x.toString();
        }
      }
      LOGGER.warn("Cannot convert value '{}' to LocalDateTime", x);
      return x.toString();
    });
  }

}
