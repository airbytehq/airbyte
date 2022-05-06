/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql;

import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class MSSQLTestDataComparator extends AdvancedTestDataComparator {

  public static final String ACTUAL_MSSQL_AIRBYTE_DATETIME_FORMAT = "yyyy-MM-dd HH:mm:ss.S";
  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

  @Override
  protected boolean compareDateTimeValues(String airbyteMessageValue, String destinationValue) {
    if (!isDateTimeValue(destinationValue)) {
      destinationValue = LocalDateTime.parse(destinationValue, DateTimeFormatter.ofPattern(ACTUAL_MSSQL_AIRBYTE_DATETIME_FORMAT)).toString();
    }
    return super.compareDateTimeValues(airbyteMessageValue, destinationValue);
  }

  @Override
  protected ZonedDateTime parseDestinationDateWithTz(String destinationValue) {
    LocalDateTime parsedDateTime = LocalDateTime.parse(destinationValue, DateTimeFormatter.ofPattern(ACTUAL_MSSQL_AIRBYTE_DATETIME_FORMAT));
    return ZonedDateTime.of(parsedDateTime, ZoneOffset.UTC);
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

}
