/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.databricks;

import io.airbyte.integrations.destination.ExtendedNameTransformer;

public class DatabricksNameTransformer extends ExtendedNameTransformer {

  @Override
  public String convertStreamName(String input) {
    return applyDefaultCase(super.convertStreamName(input));
  }

  @Override
  public String getIdentifier(String name) {
    return applyDefaultCase(super.getIdentifier(name));
  }

  @Override
  public String getTmpTableName(String streamName) {
    return applyDefaultCase(super.getTmpTableName(streamName));
  }

  @Override
  public String getRawTableName(String streamName) {
    return applyDefaultCase(super.getRawTableName(streamName));
  }

  @Override
  protected String applyDefaultCase(String input) {
    return input.toLowerCase();
  }

}
