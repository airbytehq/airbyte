/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.check.connection;

import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.StandardCheckConnectionInput;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@ActivityInterface
public interface CheckConnectionActivity {

  @Data
  @NoArgsConstructor
  @AllArgsConstructor
  class CheckConnectionInput {

    private JobRunConfig jobRunConfig;
    private IntegrationLauncherConfig launcherConfig;
    private StandardCheckConnectionInput connectionConfiguration;

  }

  @ActivityMethod
  ConnectorJobOutput runWithJobOutput(CheckConnectionInput input);

  @ActivityMethod
  StandardCheckConnectionOutput run(CheckConnectionInput input);

}
