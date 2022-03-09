/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.discover.catalog;

import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.protocol.models.AirbyteCatalog;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.temporal.TemporalUtils;
import io.temporal.activity.ActivityOptions;
import io.temporal.workflow.Workflow;
import java.time.Duration;

public class DiscoverCatalogWorkflowImpl implements DiscoverCatalogWorkflow {

  final ActivityOptions options = ActivityOptions.newBuilder()
      .setScheduleToCloseTimeout(Duration.ofHours(2))
      .setRetryOptions(TemporalUtils.NO_RETRY)
      .build();
  private final DiscoverCatalogActivity activity = Workflow.newActivityStub(DiscoverCatalogActivity.class, options);

  @Override
  public AirbyteCatalog run(final JobRunConfig jobRunConfig,
                            final IntegrationLauncherConfig launcherConfig,
                            final StandardDiscoverCatalogInput config) {
    return activity.run(jobRunConfig, launcherConfig, config);
  }

}
