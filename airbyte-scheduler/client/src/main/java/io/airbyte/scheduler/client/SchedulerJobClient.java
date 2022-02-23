/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.client;

import io.airbyte.config.DestinationConnection;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.scheduler.models.Job;
import java.io.IOException;
import java.util.List;

/**
 * Exposes a way of executing short-lived jobs as RPC calls. If it returns successfully, it
 * guarantees a job was submitted. It does not wait for that job to complete. Jobs submitted in by
 * this client are persisted in the Jobs table. It returns the full job object.
 */
public interface SchedulerJobClient {

  Job createOrGetActiveSyncJob(SourceConnection source,
                               DestinationConnection destination,
                               StandardSync standardSync,
                               String sourceDockerImage,
                               String destinationDockerImage,
                               List<StandardSyncOperation> standardSyncOperations)
      throws IOException;

  Job createOrGetActiveResetConnectionJob(DestinationConnection destination,
                                          StandardSync standardSync,
                                          String destinationDockerImage,
                                          List<StandardSyncOperation> standardSyncOperations)
      throws IOException;

}
