/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dynamodb;

import io.airbyte.integrations.base.adaptive.AdaptiveDestinationRunner;

public class DynamodbDestinationRunner {

  public static void main(final String[] args) throws Exception {
    AdaptiveDestinationRunner.baseOnEnv()
        .withOssDestination(DynamodbDestination::new)
        .withCloudDestination(DynamodbDestinationStrictEncrypt::new)
        .run(args);
  }

}
