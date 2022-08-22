/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Configs;
import io.airbyte.config.NormalizationInput;
import io.airbyte.config.NormalizationSummary;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.general.DefaultNormalizationWorker;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.normalization.NormalizationWorker;
import io.airbyte.workers.process.KubePodProcess;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.sync.ReplicationLauncherWorker;
import java.nio.file.Path;
import java.util.Optional;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class NormalizationJobOrchestrator implements JobOrchestrator<NormalizationInput> {

  private final Configs configs;
  private final WorkerConfigs workerConfigs;
  private final ProcessFactory processFactory;

  public NormalizationJobOrchestrator(final Configs configs, final WorkerConfigs workerConfigs, final ProcessFactory processFactory) {
    this.configs = configs;
    this.workerConfigs = workerConfigs;
    this.processFactory = processFactory;
  }

  @Override
  public String getOrchestratorName() {
    return "Normalization";
  }

  @Override
  public Class<NormalizationInput> getInputClass() {
    return NormalizationInput.class;
  }

  @Override
  public Optional<String> runJob() throws Exception {
    final JobRunConfig jobRunConfig = JobOrchestrator.readJobRunConfig();
    final NormalizationInput normalizationInput = readInput();

    final IntegrationLauncherConfig destinationLauncherConfig = JobOrchestrator.readAndDeserializeFile(
        Path.of(KubePodProcess.CONFIG_DIR, ReplicationLauncherWorker.INIT_FILE_DESTINATION_LAUNCHER_CONFIG),
        IntegrationLauncherConfig.class);

    log.info("Setting up normalization worker...");
    final NormalizationWorker normalizationWorker = new DefaultNormalizationWorker(
        jobRunConfig.getJobId(),
        Math.toIntExact(jobRunConfig.getAttemptId()),
        NormalizationRunnerFactory.create(
            workerConfigs,
            destinationLauncherConfig.getDockerImage(),
            processFactory,
            NormalizationRunnerFactory.NORMALIZATION_VERSION),
        configs.getWorkerEnvironment());

    log.info("Running normalization worker...");
    final Path jobRoot = WorkerUtils.getJobRoot(configs.getWorkspaceRoot(), jobRunConfig.getJobId(), jobRunConfig.getAttemptId());
    final NormalizationSummary normalizationSummary = normalizationWorker.run(normalizationInput, jobRoot);

    return Optional.of(Jsons.serialize(normalizationSummary));
  }

}
