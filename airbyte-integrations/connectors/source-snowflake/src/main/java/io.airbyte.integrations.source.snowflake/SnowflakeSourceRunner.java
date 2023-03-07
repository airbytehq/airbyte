/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.snowflake;

import static io.airbyte.integrations.source.snowflake.SnowflakeDataSourceUtils.AIRBYTE_CLOUD;
import static io.airbyte.integrations.source.snowflake.SnowflakeDataSourceUtils.AIRBYTE_OSS;
import static io.airbyte.integrations.source.snowflake.SnowflakeSource.SCHEDULED_EXECUTOR_SERVICE;

import io.airbyte.integrations.base.adaptive.AdaptiveSourceRunner;

public class SnowflakeSourceRunner {

  public static void main(final String[] args) throws Exception {
    AdaptiveSourceRunner.baseOnEnv()
        .withOssSource(() -> new SnowflakeSource(AIRBYTE_OSS))
        .withCloudSource(() -> new SnowflakeSource(AIRBYTE_CLOUD))
        .run(args);
    SCHEDULED_EXECUTOR_SERVICE.shutdownNow();
  }

}
