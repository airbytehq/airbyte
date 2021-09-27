/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

public class SnowflakeSQLNameTransformer extends ExtendedNameTransformer {

  @Override
  protected String applyDefaultCase(String input) {
    return input.toUpperCase();
  }

}
