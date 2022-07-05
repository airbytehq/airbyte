/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class PostgresTestDataComparator extends AdvancedTestDataComparator {

  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

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

  private LocalDate parseLocalDate(String dateTimeValue) {
    if (dateTimeValue != null) {
      var format = (dateTimeValue.matches(".+Z") ? POSTGRES_DATETIME_FORMAT : AIRBYTE_DATETIME_FORMAT);
      return LocalDate.parse(dateTimeValue, DateTimeFormatter.ofPattern(format));
    } else {
      return null;
    }
  }

  @Override
  protected boolean compareDateTimeValues(String expectedValue, String actualValue) {
    var destinationDate = parseLocalDate(actualValue);
    var expectedDate = LocalDate.parse(expectedValue, DateTimeFormatter.ofPattern(AIRBYTE_DATETIME_FORMAT));
    return expectedDate.equals(destinationDate);
  }

  @Override
  protected ZonedDateTime parseDestinationDateWithTz(String destinationValue) {
    return ZonedDateTime.of(LocalDateTime.parse(destinationValue, DateTimeFormatter.ofPattern(POSTGRES_DATETIME_WITH_TZ_FORMAT)), ZoneOffset.UTC);
  }

}
