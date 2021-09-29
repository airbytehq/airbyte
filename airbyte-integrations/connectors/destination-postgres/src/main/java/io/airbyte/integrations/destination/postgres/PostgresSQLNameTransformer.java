/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

public class PostgresSQLNameTransformer extends ExtendedNameTransformer {

  @Override
  protected String applyDefaultCase(String input) {
    return input.toLowerCase();
  }

}
