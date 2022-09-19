/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.discover.catalog;

import io.airbyte.config.ConnectorJobOutput;
import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.annotations.TemporalActivityStub;
import javax.inject.Singleton;

@Singleton
public class DiscoverCatalogWorkflowImpl implements DiscoverCatalogWorkflow {

  @TemporalActivityStub(activityOptionsBeanName = "discoveryActivityOptions")
  private DiscoverCatalogActivity activity;

  @Override
  public ConnectorJobOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig launcherConfig,
                                final StandardDiscoverCatalogInput config) {
    return activity.run(jobRunConfig, launcherConfig, config);
  }

}
