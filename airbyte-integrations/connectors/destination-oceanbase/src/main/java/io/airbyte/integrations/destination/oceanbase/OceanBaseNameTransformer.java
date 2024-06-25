/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.oceanbase;

import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import org.jetbrains.annotations.NotNull;


public class OceanBaseNameTransformer extends StandardNameTransformer {

  @Override
  public @NotNull String applyDefaultCase(final String input) {
    return input.toLowerCase();
  }

}
