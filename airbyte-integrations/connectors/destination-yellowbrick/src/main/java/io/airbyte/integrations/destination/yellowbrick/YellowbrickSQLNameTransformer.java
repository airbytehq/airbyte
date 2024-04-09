/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.yellowbrick;

import io.airbyte.cdk.integrations.destination.StandardNameTransformer;

public class YellowbrickSQLNameTransformer extends StandardNameTransformer {

  @Override
  public String applyDefaultCase(final String input) {
    return input.toLowerCase();
  }

}
