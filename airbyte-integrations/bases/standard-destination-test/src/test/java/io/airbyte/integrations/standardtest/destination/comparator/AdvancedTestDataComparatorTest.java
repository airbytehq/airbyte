package io.airbyte.integrations.standardtest.destination.comparator;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.standardtest.destination.comparator.parameters.AdvancedTestDataComparatorTestParameters.AssertNotSameDataArgumentProvider;
import io.airbyte.integrations.standardtest.destination.comparator.parameters.AdvancedTestDataComparatorTestParameters.AssertSameDataArgumentProvider;
import io.airbyte.integrations.standardtest.destination.comparator.parameters.EmptyNodeTestArgumentProvider;
import java.util.List;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ArgumentsSource;
import org.opentest4j.AssertionFailedError;

public class AdvancedTestDataComparatorTest {

  private AdvancedTestDataComparator comparator;

  @BeforeEach
  void init() {
    this.comparator = new AdvancedTestDataComparator();
  }

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
    final var actual = this.comparator.isJsonNodeEmpty(value);
    Assertions.assertEquals(actual, expected);
  }

}
