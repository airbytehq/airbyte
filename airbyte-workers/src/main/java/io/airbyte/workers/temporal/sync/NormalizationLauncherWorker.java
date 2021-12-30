/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.commons.io.LineGobbler;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.LoggingHelper;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.config.NormalizationInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.Worker;
import io.airbyte.workers.WorkerApp;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerException;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import java.nio.file.Path;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Collectors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class NormalizationLauncherWorker implements Worker<NormalizationInput, Void> {

  private static final Logger LOGGER = LoggerFactory.getLogger(NormalizationLauncherWorker.class);

  private static final MdcScope.Builder LOG_MDC_BUILDER = new MdcScope.Builder()
      .setLogPrefix("normalization-orchestrator")
      .setPrefixColor(LoggingHelper.Color.CYAN_BACKGROUND);

  public static final String NORMALIZATION = "normalization";
  public static final String INIT_FILE_DESTINATION_LAUNCHER_CONFIG = "destinationLauncherConfig.json";

  private final WorkerConfigs workerConfigs;
  private final ProcessFactory processFactory;
  private final String airbyteVersion;
  private final AtomicBoolean cancelled = new AtomicBoolean(false);
  private final Path workspaceRoot;
  private final IntegrationLauncherConfig destinationLauncherConfig;
  private final JobRunConfig jobRunConfig;

  private Process process;

  public NormalizationLauncherWorker(
                                     final Path workspaceRoot,
                                     final IntegrationLauncherConfig destinationLauncherConfig,
                                     final JobRunConfig jobRunConfig,
                                     final WorkerConfigs workerConfigs,
                                     final ProcessFactory processFactory,
                                     final String airbyteVersion) {
    this.workspaceRoot = workspaceRoot;
    this.destinationLauncherConfig = destinationLauncherConfig;
    this.jobRunConfig = jobRunConfig;
    this.workerConfigs = workerConfigs;
    this.processFactory = processFactory;
    this.airbyteVersion = airbyteVersion;
  }

  @Override
  public Void run(NormalizationInput normalizationInput, Path jobRoot) throws WorkerException {
    try {
      final Path jobPath = WorkerUtils.getJobRoot(workspaceRoot, jobRunConfig.getJobId(), jobRunConfig.getAttemptId());

      // we want to filter down to remove secrets, so we aren't writing over a bunch of unnecessary
      // secrets
      final Map<String, String> envMap = System.getenv().entrySet().stream()
          .filter(entry -> OrchestratorConstants.ENV_VARS_TO_TRANSFER.contains(entry.getKey()))
          .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));

      final Map<String, String> fileMap = Map.of(
          OrchestratorConstants.INIT_FILE_APPLICATION, NORMALIZATION,
          OrchestratorConstants.INIT_FILE_JOB_RUN_CONFIG, Jsons.serialize(jobRunConfig),
          OrchestratorConstants.INIT_FILE_INPUT, Jsons.serialize(normalizationInput),
          OrchestratorConstants.INIT_FILE_ENV_MAP, Jsons.serialize(envMap),
          INIT_FILE_DESTINATION_LAUNCHER_CONFIG, Jsons.serialize(destinationLauncherConfig));

      process = processFactory.create(
          "runner-" + UUID.randomUUID().toString().substring(0, 10),
          0,
          jobPath,
          "airbyte/container-orchestrator:" + airbyteVersion,
          false,
          fileMap,
          null,
          workerConfigs.getResourceRequirements(),
          Map.of(KubeProcessFactory.JOB_TYPE, KubeProcessFactory.SYNC_RUNNER),
          Map.of(
              WorkerApp.KUBE_HEARTBEAT_PORT, WorkerApp.KUBE_HEARTBEAT_PORT,
              OrchestratorConstants.PORT1, OrchestratorConstants.PORT1,
              OrchestratorConstants.PORT2, OrchestratorConstants.PORT2,
              OrchestratorConstants.PORT3, OrchestratorConstants.PORT3,
              OrchestratorConstants.PORT4, OrchestratorConstants.PORT4));

      LineGobbler.gobble(process.getInputStream(), LOGGER::info, LOG_MDC_BUILDER);
      LineGobbler.gobble(process.getErrorStream(), LOGGER::error, LOG_MDC_BUILDER);

      WorkerUtils.wait(process);

      if (process.exitValue() != 0) {
        throw new WorkerException("Non-zero exit code!");
      }
    } catch (Exception e) {
      if (cancelled.get()) {
        throw new WorkerException("Sync was cancelled.", e);
      } else {
        throw new WorkerException("Running the sync attempt failed", e);
      }
    }

    return null;
  }

  @Override
  public void cancel() {
    cancelled.set(true);

    if (process == null) {
      return;
    }

    LOGGER.debug("Closing normalization launcher process");
    WorkerUtils.gentleClose(workerConfigs, process, 1, TimeUnit.MINUTES);
    if (process.isAlive() || process.exitValue() != 0) {
      LOGGER.error("Normalization launcher process wasn't successful");
    }
  }

}
