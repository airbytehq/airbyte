/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.aws_datalake;

import io.airbyte.integrations.standardtest.destination.comparator.AdvancedTestDataComparator;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public class AwsDatalakeTestDataComparator extends AdvancedTestDataComparator {

  @Override
  protected List<String> resolveIdentifier(String identifier) {
    final List<String> result = new ArrayList<>();
    result.add(identifier);
    result.add(identifier.toLowerCase(Locale.ROOT));
    return result;
  }

}
