/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.connector;

import io.airbyte.config.StandardConnectorBuilderReadInput;
import io.airbyte.config.StandardConnectorBuilderReadOutput;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;

@ActivityInterface
public interface ConnectorBuilderReadActivity {

  @ActivityMethod
  StandardConnectorBuilderReadOutput run(JobRunConfig jobRunConfig,
                                         StandardConnectorBuilderReadInput config);

}
