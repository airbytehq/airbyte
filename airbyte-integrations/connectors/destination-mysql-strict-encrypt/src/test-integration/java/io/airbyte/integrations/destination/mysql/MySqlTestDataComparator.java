/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class MySqlTestDataComparator extends AdvancedTestDataComparator {

  private final ExtendedNameTransformer namingResolver = new MySQLNameTransformer();

  @Override
  protected List<String> resolveIdentifier(final String identifier) {
    final List<String> result = new ArrayList<>();
    final String resolved = namingResolver.getIdentifier(identifier);
    result.add(identifier);
    result.add(resolved);
    if (!resolved.startsWith("\"")) {
      result.add(resolved.toLowerCase());
    }
    return result;
  }

  @Override
  protected boolean compareBooleanValues(String firstBooleanValue, String secondBooleanValue) {
    if (secondBooleanValue.equalsIgnoreCase("true") || secondBooleanValue.equalsIgnoreCase("false")) {
      return super.compareBooleanValues(firstBooleanValue, secondBooleanValue);
    } else {
      return super.compareBooleanValues(firstBooleanValue,
              String.valueOf(secondBooleanValue.equals("1")));
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
