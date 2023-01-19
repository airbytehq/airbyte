/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.sync;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.ContainerOrchestratorConfig;
import io.airbyte.workers.WorkerConfigs;
import io.temporal.activity.ActivityExecutionContext;
import java.util.Map;
import java.util.UUID;
import java.util.function.Supplier;

public class NormalizationLauncherWorker extends LauncherWorker<NormalizationInput, NormalizationSummary> {

  public static final String NORMALIZATION = "normalization-orchestrator";
  private static final String POD_NAME_PREFIX = "orchestrator-norm";
  public static final String INIT_FILE_DESTINATION_LAUNCHER_CONFIG = "destinationLauncherConfig.json";

  public NormalizationLauncherWorker(final UUID connectionId,
                                     final IntegrationLauncherConfig destinationLauncherConfig,
                                     final JobRunConfig jobRunConfig,
                                     final WorkerConfigs workerConfigs,
                                     final ContainerOrchestratorConfig containerOrchestratorConfig,
                                     final Supplier<ActivityExecutionContext> activityContext,
                                     final Integer serverPort,
                                     final TemporalUtils temporalUtils) {
    super(
        connectionId,
        NORMALIZATION,
        POD_NAME_PREFIX,
        jobRunConfig,
        Map.of(
            INIT_FILE_DESTINATION_LAUNCHER_CONFIG, Jsons.serialize(destinationLauncherConfig)),
        containerOrchestratorConfig,
        workerConfigs.getResourceRequirements(),
        NormalizationSummary.class,
        activityContext,
        serverPort,
        temporalUtils,
        workerConfigs,
        // Normalization process will happen only on a fixed set of connectors,
        // thus they are not going to be run under custom connectors. Setting this to false.
        false);

  }

}
