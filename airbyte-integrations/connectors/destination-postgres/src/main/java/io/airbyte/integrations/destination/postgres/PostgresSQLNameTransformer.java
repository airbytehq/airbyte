/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import io.airbyte.cdk.integrations.destination.StandardNameTransformer;

public class PostgresSQLNameTransformer extends StandardNameTransformer {

  @Override
  public String applyDefaultCase(final String input) {
    return input.toLowerCase();
  }

  @Override
  // @Deprecated see https://github.com/airbytehq/airbyte/issues/35333
  // We cannot delete these method until connectors don't need old v1 raw table references for
  // migration
  public String getRawTableName(final String streamName) {
    return convertStreamName("_airbyte_raw_" + streamName.toLowerCase());
  }

}
