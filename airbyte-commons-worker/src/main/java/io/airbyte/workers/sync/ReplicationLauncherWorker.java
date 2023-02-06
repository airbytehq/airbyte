/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.sync;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.ContainerOrchestratorConfig;
import io.airbyte.workers.WorkerConfigs;
import io.temporal.activity.ActivityExecutionContext;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;

/**
 * Launches a container-orchestrator container/pod to manage the message passing for the replication
 * step. This step configs onto the container-orchestrator and retrieves logs and the output from
 * the container-orchestrator.
 */
public class ReplicationLauncherWorker extends LauncherWorker<StandardSyncInput, ReplicationOutput> {

  public static final String REPLICATION = "replication-orchestrator";
  private static final String POD_NAME_PREFIX = "orchestrator-repl";
  public static final String INIT_FILE_SOURCE_LAUNCHER_CONFIG = "sourceLauncherConfig.json";
  public static final String INIT_FILE_DESTINATION_LAUNCHER_CONFIG = "destinationLauncherConfig.json";

  public ReplicationLauncherWorker(final UUID connectionId,
                                   final ContainerOrchestratorConfig containerOrchestratorConfig,
                                   final IntegrationLauncherConfig sourceLauncherConfig,
                                   final IntegrationLauncherConfig destinationLauncherConfig,
                                   final JobRunConfig jobRunConfig,
                                   final ResourceRequirements resourceRequirements,
                                   final Supplier<ActivityExecutionContext> activityContext,
                                   final Integer serverPort,
                                   final TemporalUtils temporalUtils,
                                   final WorkerConfigs workerConfigs) {
    super(
        connectionId,
        REPLICATION,
        POD_NAME_PREFIX,
        jobRunConfig,
        Map.of(
            INIT_FILE_SOURCE_LAUNCHER_CONFIG, Jsons.serialize(sourceLauncherConfig),
            INIT_FILE_DESTINATION_LAUNCHER_CONFIG, Jsons.serialize(destinationLauncherConfig)),
        containerOrchestratorConfig,
        resourceRequirements,
        ReplicationOutput.class,
        activityContext,
        serverPort,
        temporalUtils,
        workerConfigs,
        sourceLauncherConfig.getIsCustomConnector() || destinationLauncherConfig.getIsCustomConnector());
  }

}
