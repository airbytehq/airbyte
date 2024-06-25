/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oceanbase;

import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class OceanBaseTestDataComparator extends AdvancedTestDataComparator {

  private final StandardNameTransformer namingResolver = new OceanBaseNameTransformer();

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
      return AIRBYTE_DATETIME_FORMAT;
    } else {
      return AIRBYTE_DATETIME_PARSED_FORMAT;
    }
  }

}
