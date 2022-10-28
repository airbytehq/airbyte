/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.tidb;

import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;

public class TiDBTestDataComparator extends AdvancedTestDataComparator {

  private final ExtendedNameTransformer namingResolver = new TiDBSQLNameTransformer();
  private final String TIDB_DATATIME_FORMAT = "yyyy-MM-dd HH:mm:ss.S";

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
    if (!isDateTimeValue(actualValue)) {
      actualValue = LocalDateTime.parse(actualValue, DateTimeFormatter.ofPattern(TIDB_DATATIME_FORMAT)).toString();
    }
    return super.compareDateTimeValues(expectedValue, actualValue);
  }

  @Override
  protected boolean compareBooleanValues(String firstBooleanValue, String secondBooleanValue) {
    if (secondBooleanValue.equalsIgnoreCase("true") || secondBooleanValue.equalsIgnoreCase("false")) {
      return super.compareBooleanValues(firstBooleanValue, secondBooleanValue);
    } else {
      return super.compareBooleanValues(firstBooleanValue, String.valueOf(secondBooleanValue.equals("1")));
    }
  }

}
