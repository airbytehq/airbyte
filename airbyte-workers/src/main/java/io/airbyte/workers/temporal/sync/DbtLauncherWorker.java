/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.OperatorDbtInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.WorkerApp;
import io.airbyte.workers.WorkerConfigs;
import java.util.Map;
import java.util.UUID;

public class DbtLauncherWorker extends LauncherWorker<OperatorDbtInput, Void> {

  public static final String DBT = "dbt-orchestrator";
  private static final String POD_NAME_PREFIX = "orchestrator-dbt";
  public static final String INIT_FILE_DESTINATION_LAUNCHER_CONFIG = "destinationLauncherConfig.json";

  public DbtLauncherWorker(final UUID connectionId,
                           final IntegrationLauncherConfig destinationLauncherConfig,
                           final JobRunConfig jobRunConfig,
                           final WorkerConfigs workerConfigs,
                           final WorkerApp.ContainerOrchestratorConfig containerOrchestratorConfig) {
    super(
        connectionId,
        DBT,
        POD_NAME_PREFIX,
        jobRunConfig,
        Map.of(
            INIT_FILE_DESTINATION_LAUNCHER_CONFIG, Jsons.serialize(destinationLauncherConfig)),
        containerOrchestratorConfig,
        workerConfigs.getResourceRequirements(),
        Void.class);
  }

}
