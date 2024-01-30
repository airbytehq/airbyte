/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class PostgresTestDataComparator extends AdvancedTestDataComparator {

  private final StandardNameTransformer namingResolver = new StandardNameTransformer();

  private static final String POSTGRES_DATETIME_FORMAT = "yyyy-MM-dd'T'HH:mm:ss'Z'";
  private static final String POSTGRES_DATETIME_WITH_TZ_FORMAT = "yyyy-MM-dd'T'HH:mm:ss'Z'";

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
    var destinationDate = parseLocalDate(actualValue);
    var expectedDate = LocalDate.parse(expectedValue, DateTimeFormatter.ofPattern(AIRBYTE_DATETIME_FORMAT));
    return expectedDate.equals(destinationDate);
  }

  @Override
  protected ZonedDateTime parseDestinationDateWithTz(String destinationValue) {
    return ZonedDateTime.of(LocalDateTime.parse(destinationValue,
        DateTimeFormatter.ofPattern(POSTGRES_DATETIME_WITH_TZ_FORMAT)), ZoneOffset.UTC);
  }

  private LocalDate parseLocalDate(String dateTimeValue) {
    if (dateTimeValue != null) {
      return LocalDate.parse(dateTimeValue,
          DateTimeFormatter.ofPattern(getFormat(dateTimeValue)));
    } else {
      return null;
    }
  }

  private String getFormat(String dateTimeValue) {
    if (dateTimeValue.matches(".+Z")) {
      return POSTGRES_DATETIME_FORMAT;
    } else if (dateTimeValue.contains("T")) {
      // Postgres stores array of objects as a jsobb type, i.e. array of string for all cases
      return AIRBYTE_DATETIME_FORMAT;
    } else {
      // Postgres stores datetime as datetime type after normalization
      return AIRBYTE_DATETIME_PARSED_FORMAT;
    }
  }

}
