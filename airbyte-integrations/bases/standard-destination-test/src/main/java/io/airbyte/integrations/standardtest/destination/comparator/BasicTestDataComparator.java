/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination.comparator;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BasicTestDataComparator implements TestDataComparator {

  private static final Logger LOGGER = LoggerFactory.getLogger(BasicTestDataComparator.class);

  private final Function<String, List<String>> nameResolver;

  public BasicTestDataComparator(Function<String, List<String>> nameResolver) {
    this.nameResolver = nameResolver;
  }

  @Override
  public void assertSameData(List<JsonNode> expected, List<JsonNode> actual) {
    LOGGER.info("Expected data {}", expected);
    LOGGER.info("Actual data   {}", actual);
    assertEquals(expected.size(), actual.size());
    final Iterator<JsonNode> expectedIterator = expected.iterator();
    final Iterator<JsonNode> actualIterator = actual.iterator();
    while (expectedIterator.hasNext() && actualIterator.hasNext()) {
      final JsonNode expectedData = expectedIterator.next();
      final JsonNode actualData = actualIterator.next();
      final Iterator<Map.Entry<String, JsonNode>> expectedDataIterator = expectedData.fields();
      LOGGER.info("Expected row {}", expectedData);
      LOGGER.info("Actual row   {}", actualData);
      assertEquals(expectedData.size(), actualData.size(), "Unequal row size");
      while (expectedDataIterator.hasNext()) {
        final Map.Entry<String, JsonNode> expectedEntry = expectedDataIterator.next();
        final JsonNode expectedValue = expectedEntry.getValue();
        String key = expectedEntry.getKey();
        JsonNode actualValue = ComparatorUtils.getActualValueByExpectedKey(key, actualData, nameResolver);
        LOGGER.info("For {} Expected {} vs Actual {}", key, expectedValue, actualValue);
        assertSameValue(expectedValue, actualValue);
      }
    }
  }

  // Allows subclasses to implement custom comparison asserts
  protected void assertSameValue(final JsonNode expectedValue, final JsonNode actualValue) {
    assertEquals(expectedValue, actualValue);
  }

}
