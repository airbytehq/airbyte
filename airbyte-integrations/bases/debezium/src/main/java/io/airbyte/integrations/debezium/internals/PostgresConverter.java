/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import io.debezium.spi.converter.CustomConverter;
import io.debezium.spi.converter.RelationalColumn;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.Properties;
import org.apache.kafka.connect.data.SchemaBuilder;
import org.postgresql.util.PGInterval;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresConverter implements CustomConverter<SchemaBuilder, RelationalColumn> {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresConverter.class);

  private final String[] DATE_TYPES = {"DATE", "DATETIME", "TIME", "TIMETZ", "INTERVAL", "TIMESTAMP"};
  private final String[] BIT_TYPES = {"BIT", "VARBIT"};
  private final String[] MONEY_ITEM_TYPE = {"MONEY"};
  private final String[] GEOMETRICS_TYPES = {"BOX", "CIRCLE", "LINE", "LSEG", "POINT", "POLYGON", "PATH"};
  private final String[] TEXT_TYPES =
      {"VARCHAR", "VARBINARY", "BLOB", "TEXT", "LONGTEXT", "TINYTEXT", "MEDIUMTEXT", "INVENTORY_ITEM", "TSVECTOR", "TSQUERY"};

  @Override
  public void configure(final Properties props) {}

  @Override
  public void converterFor(final RelationalColumn field, final ConverterRegistration<SchemaBuilder> registration) {
    if (Arrays.stream(DATE_TYPES).anyMatch(s -> s.equalsIgnoreCase(field.typeName()))) {
      registerDate(field, registration);
    } else if (Arrays.stream(TEXT_TYPES).anyMatch(s -> s.equalsIgnoreCase(field.typeName()))
        || Arrays.stream(GEOMETRICS_TYPES).anyMatch(s -> s.equalsIgnoreCase(field.typeName()))
        || Arrays.stream(BIT_TYPES).anyMatch(s -> s.equalsIgnoreCase(field.typeName()))) {
      registerText(field, registration);
    } else if (Arrays.stream(MONEY_ITEM_TYPE).anyMatch(s -> s.equalsIgnoreCase(field.typeName()))) {
      registerMoney(field, registration);
    }
  }

  private void registerText(final RelationalColumn field, final ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.string().optional(), x -> {
      if (x == null) {
        return DebeziumConverterUtils.convertDefaultValue(field);
      }

      if (x instanceof byte[]) {
        return new String((byte[]) x, StandardCharsets.UTF_8);
      } else {
        return x.toString();
      }
    });
  }

  private void registerDate(final RelationalColumn field, final ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.string().optional(), x -> {
      if (x == null) {
        return DebeziumConverterUtils.convertDefaultValue(field);
      } else if (x instanceof PGInterval) {
        return convertInterval((PGInterval) x);
      } else {
        return DebeziumConverterUtils.convertDate(x);
      }
    });
  }

  private String convertInterval(final PGInterval pgInterval) {
    final StringBuilder resultInterval = new StringBuilder();
    formatDateUnit(resultInterval, pgInterval.getYears(), " year ");
    formatDateUnit(resultInterval, pgInterval.getMonths(), " mons ");
    formatDateUnit(resultInterval, pgInterval.getDays(), " days ");

    formatTimeValues(resultInterval, pgInterval);
    return resultInterval.toString();
  }

  private void registerMoney(final RelationalColumn field, final ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.string().optional(), x -> {
      if (x == null) {
        return DebeziumConverterUtils.convertDefaultValue(field);
      } else if (x instanceof Double) {
        final BigDecimal result = BigDecimal.valueOf((Double) x);
        if (result.compareTo(new BigDecimal("999999999999999")) == 1
            || result.compareTo(new BigDecimal("-999999999999999")) == -1) {
          return null;
        }
        return result.toString();
      } else {
        return x.toString();
      }
    });
  }

  private void formatDateUnit(final StringBuilder resultInterval, final int dateUnit, final String s) {
    if (dateUnit != 0) {
      resultInterval
          .append(dateUnit)
          .append(s);
    }
  }

  private void formatTimeValues(final StringBuilder resultInterval, final PGInterval pgInterval) {
    if (isNegativeTime(pgInterval)) {
      resultInterval.append("-");
    }
    // TODO check if value more or less than Integer.MIN_VALUE Integer.MAX_VALUE,
    final int hours = Math.abs(pgInterval.getHours());
    final int minutes = Math.abs(pgInterval.getMinutes());
    final int seconds = Math.abs(pgInterval.getWholeSeconds());
    resultInterval.append(addFirstDigit(hours));
    resultInterval.append(hours);
    resultInterval.append(":");
    resultInterval.append(addFirstDigit(minutes));
    resultInterval.append(minutes);
    resultInterval.append(":");
    resultInterval.append(addFirstDigit(seconds));
    resultInterval.append(seconds);
  }

  private String addFirstDigit(final int hours) {
    return hours <= 9 ? "0" : "";
  }

  private boolean isNegativeTime(final PGInterval pgInterval) {
    return pgInterval.getHours() < 0
        || pgInterval.getMinutes() < 0
        || pgInterval.getWholeSeconds() < 0;
  }

}
