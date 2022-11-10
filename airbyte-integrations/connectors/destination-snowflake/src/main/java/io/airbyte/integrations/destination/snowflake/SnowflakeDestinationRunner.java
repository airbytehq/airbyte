package io.airbyte.integrations.destination.snowflake;

import io.airbyte.integrations.base.adaptive.AdaptiveDestinationRunner;
import io.airbyte.integrations.util.OssCloudEnvVarConsts;

public class SnowflakeDestinationRunner {


  public static void main(final String[] args) throws Exception {
    AdaptiveDestinationRunner.baseOnEnv()
        .withOssDestination(() -> new SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_OSS))
        .withCloudDestination(() -> new SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_CLOUD))
        .run(args);
  }


}
