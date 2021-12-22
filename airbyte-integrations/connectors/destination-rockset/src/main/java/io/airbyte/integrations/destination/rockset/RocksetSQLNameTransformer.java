/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.rockset;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

public class RocksetSQLNameTransformer extends ExtendedNameTransformer {

  @Override
  public String convertStreamName(String input) {
    return super.convertStreamName(input).toLowerCase();
  }

  @Override
  protected String applyDefaultCase(String input) {
    return input.toLowerCase();
  }

}
