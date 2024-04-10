/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.mssql;

import io.airbyte.cdk.integrations.destination.StandardNameTransformer;

public class MSSQLNameTransformer extends StandardNameTransformer {

  @Override
  public String applyDefaultCase(final String input) {
    return input.toUpperCase();
  }

}
