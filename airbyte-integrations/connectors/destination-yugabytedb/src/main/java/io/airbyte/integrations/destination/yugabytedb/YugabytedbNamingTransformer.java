/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yugabytedb;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

public class YugabytedbNamingTransformer extends ExtendedNameTransformer {

  @Override
  public String applyDefaultCase(final String input) {
    return input.toLowerCase();
  }

}
