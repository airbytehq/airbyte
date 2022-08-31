/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals;

import io.airbyte.db.jdbc.DateTimeConverter;
import io.debezium.spi.converter.CustomConverter;
import io.debezium.spi.converter.RelationalColumn;
import io.debezium.time.Conversions;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.time.LocalTime;
import java.util.Arrays;
import java.util.Locale;
import java.util.Properties;
import java.util.concurrent.TimeUnit;
import org.apache.commons.codec.binary.Hex;
import org.apache.kafka.connect.data.SchemaBuilder;
import org.postgresql.util.PGInterval;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class PostgresConverter implements CustomConverter<SchemaBuilder, RelationalColumn> {

  private static final Logger LOGGER = LoggerFactory.getLogger(PostgresConverter.class);

  private final String[] DATE_TYPES = {"DATE", "TIME", "TIMETZ", "INTERVAL", "TIMESTAMP", "TIMESTAMPTZ"};
  private final String[] BIT_TYPES = {"BIT", "VARBIT"};
  private final String[] MONEY_ITEM_TYPE = {"MONEY"};
  private final String[] GEOMETRICS_TYPES = {"BOX", "CIRCLE", "LINE", "LSEG", "POINT", "POLYGON", "PATH"};
  private final String[] TEXT_TYPES =
      {"VARCHAR", "VARBINARY", "BLOB", "TEXT", "LONGTEXT", "TINYTEXT", "MEDIUMTEXT", "INVENTORY_ITEM", "TSVECTOR", "TSQUERY", "PG_LSN"};
  private final String[] NUMERIC_TYPES = {"NUMERIC", "DECIMAL"};
  private final String BYTEA_TYPE = "BYTEA";

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
    } else if (BYTEA_TYPE.equalsIgnoreCase(field.typeName())) {
      registerBytea(field, registration);
    } else if (Arrays.stream(NUMERIC_TYPES).anyMatch(s -> s.equalsIgnoreCase(field.typeName()))) {
      registerNumber(field, registration);
    }
  }

  private void registerNumber(final RelationalColumn field, final ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.string().optional(), x -> {
      if (x == null) {
        return DebeziumConverterUtils.convertDefaultValue(field);
      }
      // Bad solution
      // We applied a solution like this for several reasons:
      // 1. Regarding #13608, CDC and nor-CDC data output format should be the same.
      // 2. In the non-CDC mode 'decimal' and 'numeric' values are put to JSON node as BigDecimal value.
      // According to Jackson Object mapper configuration, all trailing zeros are omitted and
      // numbers with decimal places are deserialized with exponent. (e.g. 1234567890.1234567 would
      // be deserialized as 1.2345678901234567E9).
      // 3. In the CDC mode 'decimal' and 'numeric' values are deserialized as a regular number (e.g.
      // 1234567890.1234567 would be deserialized as 1234567890.1234567). Numbers without
      // decimal places (e.g 1, 24, 354) are represented with trailing zero (e.g 1.0, 24.0, 354.0).
      // One of solution to align deserialization for these 2 modes is setting
      // DeserializationFeature.USE_BIG_DECIMAL_FOR_FLOATS as true for ObjectMapper. But this breaks
      // deserialization for other data-types.
      // A worked solution was to keep deserialization for non-CDC mode as it is and change it for CDC
      // one.
      // The code below strips trailing zeros for integer numbers and represents number with exponent
      // if this number has decimals point.
      final double doubleValue = Double.parseDouble(x.toString());
      var valueWithTruncatedZero = BigDecimal.valueOf(doubleValue).stripTrailingZeros().toString();
      return valueWithTruncatedZero.contains(".") ? String.valueOf(doubleValue) : valueWithTruncatedZero;
    });
  }

  private void registerBytea(final RelationalColumn field, final ConverterRegistration<SchemaBuilder> registration) {
    registration.register(SchemaBuilder.string().optional(), x -> {
      if (x == null) {
        return DebeziumConverterUtils.convertDefaultValue(field);
      }
      return "\\x" + Hex.encodeHexString((byte[]) x);
    });
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

  private int getTimePrecision(final RelationalColumn field) {
    return field.scale().orElse(-1);
  }

  // Ref :
  // https://debezium.io/documentation/reference/stable/connectors/postgresql.html#postgresql-temporal-types
  private void registerDate(final RelationalColumn field, final ConverterRegistration<SchemaBuilder> registration) {
    final var fieldType = field.typeName();

    registration.register(SchemaBuilder.string().optional(), x -> {
      if (x == null) {
        return DebeziumConverterUtils.convertDefaultValue(field);
      }
      switch (fieldType.toUpperCase(Locale.ROOT)) {
        case "TIMETZ":
          return DateTimeConverter.convertToTimeWithTimezone(x);
        case "TIMESTAMPTZ":
          return DateTimeConverter.convertToTimestampWithTimezone(x);
        case "TIMESTAMP":
          if (x instanceof final Long l) {
            if (getTimePrecision(field) <= 3) {
              return DateTimeConverter.convertToTimestamp(Conversions.toInstantFromMillis(l));
            }
            if (getTimePrecision(field) <= 6) {
              return DateTimeConverter.convertToTimestamp(Conversions.toInstantFromMicros(l));
            }
          }
          return DateTimeConverter.convertToTimestamp(x);
        case "DATE":
          if (x instanceof Integer) {
            return DateTimeConverter.convertToDate(LocalDate.ofEpochDay((Integer) x));
          }
          return DateTimeConverter.convertToDate(x);
        case "TIME":
          if (x instanceof Long) {
            if (getTimePrecision(field) <= 3) {
              long l = Math.multiplyExact((Long) x, TimeUnit.MILLISECONDS.toNanos(1));
              return DateTimeConverter.convertToTime(LocalTime.ofNanoOfDay(l));
            }
            if (getTimePrecision(field) <= 6) {
              long l = Math.multiplyExact((Long) x, TimeUnit.MICROSECONDS.toNanos(1));
              return DateTimeConverter.convertToTime(LocalTime.ofNanoOfDay(l));
            }
          }
          return DateTimeConverter.convertToTime(x);
        case "INTERVAL":
          return convertInterval((PGInterval) x);
        default:
          throw new IllegalArgumentException("Unknown field type  " + fieldType.toUpperCase(Locale.ROOT));
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
