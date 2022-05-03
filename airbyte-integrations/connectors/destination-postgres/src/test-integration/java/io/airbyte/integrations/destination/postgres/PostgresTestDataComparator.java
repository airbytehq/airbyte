/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
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

  @Override
  protected boolean compareDateTimeValues(String expectedValue, String actualValue) {
    var destinationDate = LocalDate.parse(actualValue, DateTimeFormatter.ofPattern(POSTGRES_DATETIME_FORMAT));
    var expectedDate = LocalDate.parse(expectedValue, DateTimeFormatter.ofPattern(AIRBYTE_DATETIME_FORMAT));
    return expectedDate.equals(destinationDate);
  }

  @Override
  protected ZonedDateTime parseDestinationDateWithTz(String destinationValue) {
    return ZonedDateTime.of(LocalDateTime.parse(destinationValue, DateTimeFormatter.ofPattern(POSTGRES_DATETIME_WITH_TZ_FORMAT)), ZoneOffset.UTC);
  }

}
