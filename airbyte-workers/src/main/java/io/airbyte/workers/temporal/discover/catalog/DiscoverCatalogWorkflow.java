/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.discover.catalog;

import io.airbyte.config.StandardDiscoverCatalogInput;
import io.airbyte.config.StandardDiscoverCatalogOutput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.temporal.workflow.WorkflowInterface;
import io.temporal.workflow.WorkflowMethod;

@WorkflowInterface
public interface DiscoverCatalogWorkflow {

  @WorkflowMethod
  StandardDiscoverCatalogOutput run(JobRunConfig jobRunConfig,
                                    IntegrationLauncherConfig launcherConfig,
                                    StandardDiscoverCatalogInput config);

}
