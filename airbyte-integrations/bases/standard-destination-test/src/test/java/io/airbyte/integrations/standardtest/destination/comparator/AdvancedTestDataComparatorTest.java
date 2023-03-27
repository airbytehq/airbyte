package io.airbyte.integrations.standardtest.destination.comparator;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.standardtest.destination.comparator.parameters.AdvancedTestDataComparatorTestParameters.AssertNotSameDataArgumentProvider;
import io.airbyte.integrations.standardtest.destination.comparator.parameters.AdvancedTestDataComparatorTestParameters.AssertSameDataArgumentProvider;
import io.airbyte.integrations.standardtest.destination.comparator.parameters.EmptyNodeTestArgumentProvider;
import io.airbyte.integrations.standardtest.destination.comparator.parameters.IsDateTimeValueTestArgumentProvider;
import io.airbyte.integrations.standardtest.destination.comparator.parameters.IsDateTimeWithTzTestArgumentProvider;
import io.airbyte.integrations.standardtest.destination.comparator.parameters.IsDateValueTestArgumentProvider;
import io.airbyte.integrations.standardtest.destination.comparator.parameters.IsNumericTestArgumentProvider;
import io.airbyte.integrations.standardtest.destination.comparator.parameters.IsTimeWithTimeZoneTestArgumentProvider;
import io.airbyte.integrations.standardtest.destination.comparator.parameters.IsTimeWithoutTimeZoneTestArgumentProvider;
import java.util.List;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ArgumentsSource;
import org.opentest4j.AssertionFailedError;

public class AdvancedTestDataComparatorTest {

  private static final AdvancedTestDataComparator comparator = new AdvancedTestDataComparator();

  @ParameterizedTest
  @ArgumentsSource(AssertSameDataArgumentProvider.class)
  public void testAssertSameData(final List<JsonNode> first, final List<JsonNode> second) {
    comparator.assertSameData(first, second);
  }

  @ParameterizedTest
  @ArgumentsSource(AssertNotSameDataArgumentProvider.class)
  public void testAssertNotSameData(final List<JsonNode> first, final List<JsonNode> second) {
    Assertions.assertThrows(AssertionFailedError.class, () -> comparator.assertSameData(first, second));
    Assertions.assertThrows(AssertionFailedError.class, () -> comparator.assertSameData(second, first));
  }

  @ParameterizedTest
  @ArgumentsSource(EmptyNodeTestArgumentProvider.class)
  public void testIsJsonNodeEmpty(final JsonNode value, final boolean expected) {
    final var actual = AdvancedTestDataComparator.isJsonNodeEmpty(value);
    Assertions.assertEquals(expected, actual);
  }

  @ParameterizedTest
  @ArgumentsSource(IsNumericTestArgumentProvider.class)
  public void testIsNumeric(final String value, final boolean expected) {
    final var actual = AdvancedTestDataComparator.isNumeric(value);
    Assertions.assertEquals(expected, actual);
  }

  @ParameterizedTest
  @ArgumentsSource(IsDateTimeWithTzTestArgumentProvider.class)
  public void testIsDateTimeWithTzValue(final String value, final boolean expected) {
    final var actual = AdvancedTestDataComparator.isDateTimeWithTzValue(value);
    Assertions.assertEquals(expected, actual);
  }

  @ParameterizedTest
  @ArgumentsSource(IsDateTimeValueTestArgumentProvider.class)
  public void testIsDateTimeValue(final String value, final boolean expected) {
    final var actual = AdvancedTestDataComparator.isDateTimeValue(value);
    Assertions.assertEquals(expected, actual);
  }

  @ParameterizedTest
  @ArgumentsSource(IsTimeWithTimeZoneTestArgumentProvider.class)
  public void testIsTimeWithTimezone(final String value, final boolean expected) {
    final var actual = AdvancedTestDataComparator.isTimeWithTimezone(value);
    Assertions.assertEquals(expected, actual);
  }

  @ParameterizedTest
  @ArgumentsSource(IsTimeWithoutTimeZoneTestArgumentProvider.class)
  public void testIsTimeWithoutTimezone(final String value, final boolean expected) {
    final var actual = AdvancedTestDataComparator.isTimeWithoutTimezone(value);
    Assertions.assertEquals(expected, actual);
  }

  @ParameterizedTest
  @ArgumentsSource(IsDateValueTestArgumentProvider.class)
  public void testIsDateValue(final String value, final boolean expected) {
    final var actual = AdvancedTestDataComparator.isDateValue(value);
    Assertions.assertEquals(expected, actual);
  }

}
