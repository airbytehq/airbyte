/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.discover.catalog;

import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.temporal.activity.ActivityInterface;
import io.temporal.activity.ActivityMethod;

@ActivityInterface
public interface DiscoverCatalogActivity {

  @ActivityMethod
  ConnectorJobOutput run(JobRunConfig jobRunConfig,
                         IntegrationLauncherConfig launcherConfig,
                         StandardDiscoverCatalogInput config);

}
