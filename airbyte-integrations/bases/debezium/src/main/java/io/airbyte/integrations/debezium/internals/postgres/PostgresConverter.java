/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.debezium.internals.postgres;

import static io.airbyte.db.jdbc.DateTimeConverter.convertToDate;
import static io.airbyte.db.jdbc.DateTimeConverter.convertToTime;
import static io.airbyte.db.jdbc.DateTimeConverter.convertToTimestamp;
import static io.airbyte.db.jdbc.DateTimeConverter.convertToTimestampWithTimezone;
import static org.apache.kafka.connect.data.Schema.OPTIONAL_BOOLEAN_SCHEMA;
import static org.apache.kafka.connect.data.Schema.OPTIONAL_FLOAT64_SCHEMA;
import static org.apache.kafka.connect.data.Schema.OPTIONAL_INT64_SCHEMA;
import static org.apache.kafka.connect.data.Schema.OPTIONAL_STRING_SCHEMA;

import io.airbyte.db.jdbc.DateTimeConverter;
import io.airbyte.integrations.debezium.internals.DebeziumConverterUtils;
import io.debezium.spi.converter.CustomConverter;
import io.debezium.spi.converter.RelationalColumn;
import io.debezium.time.Conversions;
import java.math.BigDecimal;
import java.nio.charset.StandardCharsets;
import java.sql.SQLException;
import java.time.LocalDate;
import java.time.LocalTime;
import java.time.OffsetTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.Properties;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;
import org.apache.commons.codec.binary.Hex;
import org.apache.kafka.connect.data.SchemaBuilder;
import org.postgresql.jdbc.PgArray;
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
  private final String[] ARRAY_TYPES = {"_NAME", "_NUMERIC", "_BYTEA", "_MONEY", "_BIT", "_DATE", "_TIME", "_TIMETZ", "_TIMESTAMP", "_TIMESTAMPTZ"};
  private final String BYTEA_TYPE = "BYTEA";

  // Debezium is manually setting the variable scale decimal length (precision)
  // of numeric_array columns to 131089 if not specified. e.g: NUMERIC vs NUMERIC(38,0)
  // https://github.com/debezium/debezium/blob/main/debezium-connector-postgres/src/main/java/io/debezium/connector/postgresql/PostgresValueConverter.java#L113
  private final int VARIABLE_SCALE_DECIMAL_LENGTH = 131089;

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
    } else if (Arrays.stream(ARRAY_TYPES).anyMatch(s -> s.equalsIgnoreCase(field.typeName()))) {
      registerArray(field, registration);
    }
  }

  private void registerArray(final RelationalColumn field, final ConverterRegistration<SchemaBuilder> registration) {
    final String fieldType = field.typeName().toUpperCase();
    final SchemaBuilder arraySchema = switch (fieldType) {
      case "_NUMERIC" -> {
        // If a numeric_array column does not have variable precision AND scale is 0
        // then we know the precision and scale are purposefully chosen
        if (numericArrayColumnPrecisionIsNotVariable(field) && field.scale().orElse(0) == 0) {
          yield SchemaBuilder.array(OPTIONAL_INT64_SCHEMA);
        } else {
          yield SchemaBuilder.array(OPTIONAL_FLOAT64_SCHEMA);
        }
      }
      case "_MONEY" -> SchemaBuilder.array(OPTIONAL_FLOAT64_SCHEMA);
      case "_NAME", "_DATE", "_TIME", "_TIMESTAMP", "_TIMESTAMPTZ", "_TIMETZ", "_BYTEA" -> SchemaBuilder.array(OPTIONAL_STRING_SCHEMA);
      case "_BIT" -> SchemaBuilder.array(OPTIONAL_BOOLEAN_SCHEMA);
      default -> SchemaBuilder.array(OPTIONAL_STRING_SCHEMA);
    };
    registration.register(arraySchema, x -> convertArray(x, field));
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

  private Object convertArray(final Object x, final RelationalColumn field) {
    if (x == null) {
      return DebeziumConverterUtils.convertDefaultValue(field);
    }
    final String fieldType = field.typeName().toUpperCase();
    switch (fieldType) {
      // debezium currently cannot handle MONEY[] datatype and it's not implemented
      case "_MONEY":
        // PgArray.getArray() trying to convert to Double instead of PgMoney
        // due to incorrect type mapping in the postgres driver
        // https://github.com/pgjdbc/pgjdbc/blob/d5ed52ef391670e83ae5265af2f7301c615ce4ca/pgjdbc/src/main/java/org/postgresql/jdbc/TypeInfoCache.java#L88
        // and throws an exception, so a custom implementation of converting to String is used to get the
        // value as is
        final String nativeMoneyValue = ((PgArray) x).toString();
        final String substringM = Objects.requireNonNull(nativeMoneyValue).substring(1, nativeMoneyValue.length() - 1);
        final char currency = substringM.charAt(0);
        final String regex = "\\" + currency;
        final List<String> myListM = new ArrayList<>(Arrays.asList(substringM.split(regex)));
        return myListM.stream()
            // since the separator is the currency sign, all extra characters must be removed except for numbers
            // and dots
            .map(val -> val.replaceAll("[^\\d.]", ""))
            .filter(money -> !money.isEmpty())
            .map(Double::valueOf)
            .collect(Collectors.toList());
      case "_NUMERIC":
        return Arrays.stream(getArray(x)).map(value -> {
          if (value == null) {
            return null;
          } else {
            if (numericArrayColumnPrecisionIsNotVariable(field) && field.scale().orElse(0) == 0) {
              return Long.parseLong(value.toString());
            } else {
              return Double.valueOf(value.toString());
            }
          }
        }).collect(Collectors.toList());
      case "_TIME":
        return Arrays.stream(getArray(x)).map(value -> value == null ? null : convertToTime(value)).collect(Collectors.toList());
      case "_DATE":
        return Arrays.stream(getArray(x)).map(value -> value == null ? null : convertToDate(value)).collect(Collectors.toList());
      case "_TIMESTAMP":
        return Arrays.stream(getArray(x)).map(value -> value == null ? null : convertToTimestamp(value)).collect(Collectors.toList());
      case "_TIMESTAMPTZ":
        return Arrays.stream(getArray(x)).map(value -> value == null ? null : convertToTimestampWithTimezone(value)).collect(Collectors.toList());
      case "_TIMETZ":

        final List<String> timetzArr = new ArrayList<>();
        final String nativeValue = ((PgArray) x).toString();
        final String substring = Objects.requireNonNull(nativeValue).substring(1, nativeValue.length() - 1);
        final List<String> times = new ArrayList<>(Arrays.asList(substring.split(",")));
        final DateTimeFormatter format = DateTimeFormatter.ofPattern("HH:mm:ss[.SSSSSS]X");

        times.forEach(s -> {
          if (s.equalsIgnoreCase("NULL")) {
            timetzArr.add(null);
          } else {
            final OffsetTime parsed = OffsetTime.parse(s, format);
            timetzArr.add(DateTimeConverter.convertToTimeWithTimezone(parsed));
          }
        });
        return timetzArr;
      case "_BYTEA":
        return Arrays.stream(getArray(x)).map(value -> Base64.getEncoder().encodeToString((byte[]) value)).collect(Collectors.toList());
      case "_BIT":
        return Arrays.stream(getArray(x)).map(value -> (Boolean) value).collect(Collectors.toList());
      case "_NAME":
        return Arrays.stream(getArray(x)).map(value -> (String) value).collect(Collectors.toList());
      default:
        throw new RuntimeException("Unknown array type detected " + fieldType);
    }
  }

  private Object[] getArray(final Object x) {
    try {
      return (Object[]) ((PgArray) x).getArray();
    } catch (final SQLException e) {
      LOGGER.error("Failed to convert PgArray:" + e);
      throw new RuntimeException(e);
    }
  }

  private int getTimePrecision(final RelationalColumn field) {
    return field.scale().orElse(-1);
  }

  // Ref :
  // https://debezium.io/documentation/reference/2.2/connectors/postgresql.html#postgresql-temporal-types
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
              return convertToTimestamp(Conversions.toInstantFromMillis(l));
            }
            if (getTimePrecision(field) <= 6) {
              return convertToTimestamp(Conversions.toInstantFromMicros(l));
            }
          }
          return convertToTimestamp(x);
        case "DATE":
          if (x instanceof Integer) {
            return convertToDate(LocalDate.ofEpochDay((Integer) x));
          }
          return convertToDate(x);
        case "TIME":
          return resolveTime(field, x);
        case "INTERVAL":
          return convertInterval((PGInterval) x);
        default:
          throw new IllegalArgumentException("Unknown field type  " + fieldType.toUpperCase(Locale.ROOT));
      }
    });
  }

  private String resolveTime(RelationalColumn field, Object x) {
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

  private boolean numericArrayColumnPrecisionIsNotVariable(final RelationalColumn column) {
    return column.length().orElse(VARIABLE_SCALE_DECIMAL_LENGTH) != VARIABLE_SCALE_DECIMAL_LENGTH;
  }

}
