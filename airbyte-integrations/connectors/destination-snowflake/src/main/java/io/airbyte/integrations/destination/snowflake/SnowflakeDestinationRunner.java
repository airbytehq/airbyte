/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.integrations.destination.snowflake.SnowflakeDestination.SCHEDULED_EXECUTOR_SERVICE;

import io.airbyte.integrations.base.adaptive.AdaptiveDestinationRunner;

public class SnowflakeDestinationRunner {

  public static void main(final String[] args) throws Exception {
    AdaptiveDestinationRunner.baseOnEnv()
        .withOssDestination(() -> new SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_OSS))
        .withCloudDestination(() -> new SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_CLOUD))
        .run(args);
    SCHEDULED_EXECUTOR_SERVICE.shutdownNow();
  }

}
