/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClickhouseTestDataComparator extends AdvancedTestDataComparator {

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickhouseTestDataComparator.class);
  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  private static final String CLICKHOUSE_DATETIME_WITH_TZ_FORMAT = "yyyy-MM-dd'T'HH:mm:ss.SSSX";

  // https://clickhouse.com/docs/en/sql-reference/data-types/date32/
  private final LocalDate minSupportedDate = LocalDate.parse("1970-01-01");
  private final LocalDate maxSupportedDate = LocalDate.parse("2149-06-06");
  private final ZonedDateTime minSupportedDateTime = ZonedDateTime.parse(
      "1925-01-01T00:00:00.000Z");
  private final ZonedDateTime maxSupportedDateTime = ZonedDateTime.parse(
      "2283-11-10T20:23:45.000Z");

  @Override
  protected List<String> resolveIdentifier(final String identifier) {
    final List<String> result = new ArrayList<>();
    final String resolved = namingResolver.getIdentifier(identifier);
    result.add(identifier);
    result.add(resolved);
    if (!resolved.startsWith("\"")) {
      result.add(resolved.toLowerCase());
      result.add(resolved.toUpperCase());
    }
    return result;
  }

  @Override
  protected boolean compareNumericValues(final String firstNumericValue,
                                         final String secondNumericValue) {
    // clickhouse stores double 1.14 as 1.1400000000000001
    // https://clickhouse.com/docs/en/sql-reference/data-types/float/
    double epsilon = 0.000000000000001d;

    double firstValue = Double.parseDouble(firstNumericValue);
    double secondValue = Double.parseDouble(secondNumericValue);

    return Math.abs(firstValue - secondValue) < epsilon;
  }

  @Override
  protected boolean compareBooleanValues(final String firstValue, final String secondValue) {
    return parseBool(firstValue) == parseBool(secondValue);
  }

  @Override
  protected boolean compareDateValues(final String airbyteMessageValue,
                                      final String destinationValue) {
    final LocalDate expectedDate = LocalDate.parse(airbyteMessageValue);
    final LocalDate actualDate = LocalDate.parse(destinationValue);

    if (expectedDate.isBefore(minSupportedDate) || expectedDate.isAfter(maxSupportedDate)) {
      // inserting any dates that are out of supported range causes registers overflow in clickhouseDB,
      // so actually you end up with unpredicted values, more
      // https://clickhouse.com/docs/en/sql-reference/data-types/date32
      LOGGER.warn(
          "Test value is out of range and would be corrupted by Snowflake, so we skip this verification");
      return true;
    }

    return actualDate.equals(expectedDate);
  }

  @Override
  protected boolean compareDateTimeWithTzValues(final String airbyteMessageValue,
                                                final String destinationValue) {
    try {
      ZonedDateTime airbyteDate = ZonedDateTime.parse(airbyteMessageValue,
          getAirbyteDateTimeWithTzFormatter()).withZoneSameInstant(ZoneOffset.UTC);
      ZonedDateTime destinationDate = parseDestinationDateWithTz(destinationValue);

      if (airbyteDate.isBefore(minSupportedDateTime) || airbyteDate.isAfter(maxSupportedDateTime)) {
        // inserting any dates that are out of supported range causes registers overflow in clickhouseDB,
        // so actually you end up with unpredicted values, more
        // https://clickhouse.com/docs/en/sql-reference/data-types/datetime64
        LOGGER.warn(
            "Test value is out of range and would be corrupted by Snowflake, so we skip this verification");
        return true;
      }
      return airbyteDate.equals(destinationDate);
    } catch (DateTimeParseException e) {
      LOGGER.warn(
          "Fail to convert values to ZonedDateTime. Try to compare as text. Airbyte value({}), Destination value ({}). Exception: {}",
          airbyteMessageValue, destinationValue, e);
      return compareTextValues(airbyteMessageValue, destinationValue);
    }
  }

  @Override
  protected ZonedDateTime parseDestinationDateWithTz(final String destinationValue) {
    return ZonedDateTime.parse(destinationValue,
        DateTimeFormatter.ofPattern(CLICKHOUSE_DATETIME_WITH_TZ_FORMAT)).withZoneSameInstant(
            ZoneOffset.UTC);
  }

  @Override
  protected boolean compareDateTimeValues(final String airbyteMessageValue,
                                          final String destinationValue) {
    final LocalDateTime expectedDateTime = LocalDateTime.parse(airbyteMessageValue);
    final LocalDateTime actualDateTime = LocalDateTime.parse(destinationValue,
        DateTimeFormatter.ofPattern(CLICKHOUSE_DATETIME_WITH_TZ_FORMAT));

    if (expectedDateTime.isBefore(minSupportedDateTime.toLocalDateTime())
        || expectedDateTime.isAfter(maxSupportedDateTime.toLocalDateTime())) {
      // inserting any dates that are out of supported range causes registers overflow in clickhouseDB,
      // so actually you end up with unpredicted values, more
      // https://clickhouse.com/docs/en/sql-reference/data-types/datetime64
      LOGGER.warn(
          "Test value is out of range and would be corrupted by Snowflake, so we skip this verification");
      return true;
    }

    return expectedDateTime.equals(actualDateTime);
  }

  private boolean parseBool(final String valueAsString) {
    // boolen as a String may be returned as true\false and as 0\1
    // https://clickhouse.com/docs/en/sql-reference/data-types/boolean
    try {
      return Integer.parseInt(valueAsString) > 0;
    } catch (final NumberFormatException ex) {
      return Boolean.parseBoolean(valueAsString);
    }

  }

}
