/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import io.airbyte.integrations.destination.ExtendedNameTransformer;
import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClickhouseTestDataComparator extends AdvancedTestDataComparator {

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickhouseTestDataComparator.class);
  private final ExtendedNameTransformer namingResolver = new ExtendedNameTransformer();

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
  protected boolean compareNumericValues(final String firstNumericValue, final String secondNumericValue) {
    // clickhouse stores double 1.14 as 1.1400000000000001
    //https://clickhouse.com/docs/en/sql-reference/data-types/float/
    double epsilon = 0.000000000000001d;

    double firstValue = Double.parseDouble(firstNumericValue);
    double secondValue = Double.parseDouble(secondNumericValue);

    return Math.abs(firstValue - secondValue) < epsilon;
  }

  @Override
  protected boolean compareBooleanValues(final String firstValue, final String secondValue) {
    return parseBool(firstValue) == parseBool(secondValue);
  }


  private boolean parseBool(final String valueAsString){
    // boolen as a String may be returned as true\false and as 0\1
    // https://clickhouse.com/docs/en/sql-reference/data-types/boolean
    try {
      return Integer.parseInt(valueAsString) > 0;
    } catch (final NumberFormatException ex){
      return Boolean.parseBoolean(valueAsString);
    }

  }

}
