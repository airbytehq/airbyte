/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.standardtest.destination.comparator;

import com.fasterxml.jackson.databind.JsonNode;
import java.util.List;

public interface TestDataComparator {

  void assertSameData(final List<JsonNode> expected, final List<JsonNode> actual);

}
