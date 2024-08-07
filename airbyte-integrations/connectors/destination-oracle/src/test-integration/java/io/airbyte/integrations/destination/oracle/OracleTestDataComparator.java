/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oracle;

import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import io.airbyte.cdk.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.util.ArrayList;
import java.util.List;

public class OracleTestDataComparator extends AdvancedTestDataComparator {

  private final StandardNameTransformer namingResolver = new OracleNameTransformer();

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

}
