/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.rockset;

import io.airbyte.integrations.destination.StandardNameTransformer;

public class RocksetSQLNameTransformer extends StandardNameTransformer {

  @Override
  public String convertStreamName(String input) {
    return super.convertStreamName(input).toLowerCase();
  }

  @Override
  public String applyDefaultCase(String input) {
    return input.toLowerCase();
  }

}
