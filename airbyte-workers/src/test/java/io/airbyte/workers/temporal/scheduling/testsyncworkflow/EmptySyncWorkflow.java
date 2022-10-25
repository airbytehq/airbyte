/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.testsyncworkflow;

import io.airbyte.commons.temporal.scheduling.SyncWorkflow;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import java.util.UUID;

public class EmptySyncWorkflow implements SyncWorkflow {

  @Override
  public StandardSyncOutput run(final JobRunConfig jobRunConfig,
                                final IntegrationLauncherConfig sourceLauncherConfig,
                                final IntegrationLauncherConfig destinationLauncherConfig,
                                final StandardSyncInput syncInput,
                                final UUID connectionId) {

    return new StandardSyncOutput();
  }

}
