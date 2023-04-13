/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bytehouse;

import io.airbyte.integrations.destination.StandardNameTransformer;

public class BytehouseSQLNameTransformer extends StandardNameTransformer {

  @Override
  public String applyDefaultCase(final String input) {
    return input.toLowerCase();
  }

}
