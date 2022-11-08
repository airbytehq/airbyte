/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.exasol;

import io.airbyte.integrations.destination.ExtendedNameTransformer;
import java.util.UUID;

public class ExasolSQLNameTransformer extends ExtendedNameTransformer {

  @Override
  public String applyDefaultCase(final String input) {
    return input.toUpperCase();
  }

  @Override
  public String getRawTableName(final String streamName) {
    return convertStreamName("airbyte_raw_" + streamName);
  }

  @Override
  public String getTmpTableName(final String streamName) {
    return convertStreamName("airbyte_tmp_" + streamName + "_" + UUID.randomUUID().toString().replace("-", ""));
  }

  @Override
  public String convertStreamName(final String input) {
    return "\"" + super.convertStreamName(input) + "\"";
  }

}
