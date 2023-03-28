/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination.comparator;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.standardtest.destination.comparator.parameters.AdvancedTestDataComparatorTestParameters.AssertSameDataArgumentProvider;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ArgumentsSource;

public class BasicTestDataComparatorTest {

  private BasicTestDataComparator comparator;

  @BeforeEach
  void init() {
    this.comparator = new BasicTestDataComparator(List::of);
  }

  @ParameterizedTest
  @ArgumentsSource(AssertSameDataArgumentProvider.class)
  public void testAssertSameData(final List<JsonNode> first, final List<JsonNode> second) {
    comparator.assertSameData(first, second);
  }

}
