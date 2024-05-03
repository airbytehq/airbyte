/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore;

import io.airbyte.cdk.integrations.destination.StandardNameTransformer;
import org.jetbrains.annotations.NotNull;

public class SingleStoreNameTransformer extends StandardNameTransformer {

  @Override
  public String getIdentifier(final String name) {
    return truncate(super.getIdentifier(name));
  }

  @Override
  public String convertStreamName(String input) {
    return truncate(super.convertStreamName(input));
  }

  @NotNull
  @Override
  public String applyDefaultCase(final String input) {
    return input.toLowerCase();
  }

  // SingleStore support 256 max length of names but set 64 as version below than 8.5.0 is limited by
  // 64
  private String truncate(String str) {
    return str.substring(0, Math.min(str.length(), 64));
  }

}
