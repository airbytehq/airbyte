/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg;

import static io.airbyte.cdk.integrations.base.adaptive.AdaptiveDestinationRunner.baseOnEnv;

public class IcebergDestinationRunner {

  public static void main(String[] args) throws Exception {
    baseOnEnv()
        .withOssDestination(IcebergOssDestination::new)
        .withCloudDestination(IcebergCloudDestination::new)
        .run(args);
  }

}
