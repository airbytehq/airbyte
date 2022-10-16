/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql;

import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.time.LocalDate;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class MSSQLTestDataComparator extends AdvancedTestDataComparator {

  private static final Logger LOGGER = LoggerFactory.getLogger(MSSQLTestDataComparator.class);
  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  @Override
  protected boolean compareDateTimeWithTzValues(final String airbyteMessageValue,
                                                final String destinationValue) {
    try {
      final ZonedDateTime airbyteDate = ZonedDateTime.parse(airbyteMessageValue,
          getAirbyteDateTimeWithTzFormatter());

      final ZonedDateTime destinationDate = ZonedDateTime.parse(destinationValue,
          getAirbyteDateTimeParsedWithTzFormatter());
      return airbyteDate.equals(destinationDate);
    } catch (DateTimeParseException e) {
      LOGGER.warn(
          "Fail to convert values to ZonedDateTime. Try to compare as text. Airbyte value({}), Destination value ({}). Exception: {}",
          airbyteMessageValue, destinationValue, e);
      return compareTextValues(airbyteMessageValue, destinationValue);
    }
  }

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
  protected boolean compareDateTimeValues(String expectedValue, String actualValue) {
    final var destinationDate = parseLocalDateTime(actualValue);
    final var expectedDate = LocalDate.parse(expectedValue,
        DateTimeFormatter.ofPattern(AIRBYTE_DATETIME_FORMAT));
    return expectedDate.equals(destinationDate);
  }

  private LocalDate parseLocalDateTime(String dateTimeValue) {
    if (dateTimeValue != null) {
      return LocalDate.parse(dateTimeValue,
          DateTimeFormatter.ofPattern(getFormat(dateTimeValue)));
    } else {
      return null;
    }
  }

  private String getFormat(String dateTimeValue) {
    if (dateTimeValue.contains("T")) {
      // MsSql stores array of objects as a jsobb type, i.e. array of string for all cases
      return AIRBYTE_DATETIME_FORMAT;
    } else {
      // MsSql stores datetime as datetime type after normalization
      return AIRBYTE_DATETIME_PARSED_FORMAT;
    }
  }

}
