/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake;

import static io.airbyte.integrations.destination.snowflake.SnowflakeDestination.SCHEDULED_EXECUTOR_SERVICE;

import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler;
import io.airbyte.cdk.integrations.base.IntegrationRunner;
import io.airbyte.cdk.integrations.base.adaptive.AdaptiveDestinationRunner;
import net.snowflake.client.core.SFStatement;
import net.snowflake.client.jdbc.SnowflakeSQLException;

public class SnowflakeDestinationRunner {

  public static void main(final String[] args) throws Exception {
    IntegrationRunner.addOrphanedThreadFilter((Thread t) -> {
      for (StackTraceElement stackTraceElement : IntegrationRunner.getThreadCreationStack(t).getStack()) {
        if (stackTraceElement.getClassName().equals(SFStatement.class.getCanonicalName()) && stackTraceElement.getMethodName().equals("close")) {
          return false;
        }
      }
      return true;
    });
    AirbyteExceptionHandler.addThrowableForDeinterpolation(SnowflakeSQLException.class);
    AdaptiveDestinationRunner.baseOnEnv()
        .withOssDestination(() -> new SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_OSS))
        .withCloudDestination(() -> new SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_CLOUD))
        .run(args);
    SCHEDULED_EXECUTOR_SERVICE.shutdownNow();
  }

}
