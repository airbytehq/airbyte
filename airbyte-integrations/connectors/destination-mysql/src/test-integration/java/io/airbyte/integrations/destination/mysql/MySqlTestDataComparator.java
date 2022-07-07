/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mysql;

import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
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
      return super.compareBooleanValues(firstBooleanValue, String.valueOf(secondBooleanValue.equals("1")));
    }
  }

}
