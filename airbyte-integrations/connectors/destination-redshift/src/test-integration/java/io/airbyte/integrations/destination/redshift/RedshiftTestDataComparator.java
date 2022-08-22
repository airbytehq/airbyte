/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift;

import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.format.DateTimeParseException;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class RedshiftTestDataComparator extends AdvancedTestDataComparator {

  private static final Logger LOGGER = LoggerFactory.getLogger(RedshiftTestDataComparator.class);

  private final RedshiftSQLNameTransformer namingResolver = new RedshiftSQLNameTransformer();

  protected static final String REDSHIFT_DATETIME_WITH_TZ_FORMAT = "yyyy-MM-dd HH:mm:ssX";

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
  protected boolean compareDateTimeWithTzValues(final String airbyteMessageValue,
                                                final String destinationValue) {
    try {
      final ZonedDateTime airbyteDate = ZonedDateTime.parse(airbyteMessageValue,
          getAirbyteDateTimeWithTzFormatter()).withZoneSameInstant(
              ZoneOffset.UTC);

      final ZonedDateTime destinationDate = ZonedDateTime.parse(destinationValue,
          DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ssX"));
      return airbyteDate.equals(destinationDate);
    } catch (DateTimeParseException e) {
      LOGGER.warn(
          "Fail to convert values to ZonedDateTime. Try to compare as text. Airbyte value({}), Destination value ({}). Exception: {}",
          airbyteMessageValue, destinationValue, e);
      return compareTextValues(airbyteMessageValue, destinationValue);
    }
  }

  @Override
  protected boolean compareDateTimeValues(String expectedValue, String actualValue) {
    var destinationDate = parseLocalDateTime(actualValue);
    var expectedDate = LocalDate.parse(expectedValue,
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
      // MySql stores array of objects as a jsonb type, i.e. array of string for all cases
      return AIRBYTE_DATETIME_FORMAT;
    } else {
      // MySql stores datetime as datetime type after normalization
      return AIRBYTE_DATETIME_PARSED_FORMAT;
    }
  }

}
