/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import io.airbyte.cdk.integrations.base.adaptive.AdaptiveDestinationRunner;

public class PostgresDestinationRunner {

  public static void main(final String[] args) throws Exception {

    AdaptiveDestinationRunner.baseOnEnv()
        .withOssDestination(() -> new PostgresDestination())
        .withCloudDestination(() -> new PostgresDestinationStrictEncrypt())
        .run(args);
  }

}
