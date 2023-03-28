/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination.comparator;

import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

public class TestClickhouseTestDataComparator {

  private static final ClickhouseTestDataComparator comparator = new ClickhouseTestDataComparator();

  private static final String REALLY_BIG_NUMBER = "1000000000000000000000000000000000000000000000000000000000000000000000"
      + "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
      + "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
      + "0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
      + "00000000000000000000000000000000.1234";

  @ParameterizedTest
  @ValueSource(strings = {REALLY_BIG_NUMBER, "1", "100", "-15", "42.32", "-34.43"})
  public void testCompareNumericValues(final String number) {
    Assertions.assertTrue(comparator.compareNumericValues(number, number));
  }

  @ParameterizedTest
  @ValueSource(doubles = {100.0, -2342.2, 1.14, Double.MAX_VALUE, Double.MIN_VALUE})
  public void testAlmostEqualNumber(final double value) {
    final double minDiff = Math.ulp(value);
    final String stringValue = String.valueOf(value);
    final String less = String.valueOf(value - minDiff);
    final String more = String.valueOf(value + minDiff);
    Assertions.assertTrue(comparator.compareNumericValues(stringValue, stringValue));
    Assertions.assertFalse(comparator.compareNumericValues(stringValue, less));
    Assertions.assertFalse(comparator.compareNumericValues(stringValue, more));
  }

}
