/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.teradata;

import io.airbyte.cdk.integrations.destination.StandardNameTransformer;

public class TeradataNameTransformer extends StandardNameTransformer {

  @Override
  public String getRawTableName(final String streamName) {
    return convertStreamName(streamName).toLowerCase();
  }

}
