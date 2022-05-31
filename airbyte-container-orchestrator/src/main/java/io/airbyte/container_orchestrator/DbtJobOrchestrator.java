/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.config.Configs;
import io.airbyte.config.OperatorDbtInput;
import io.airbyte.scheduler.models.IntegrationLauncherConfig;
import io.airbyte.scheduler.models.JobRunConfig;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.general.DbtTransformationRunner;
import io.airbyte.workers.general.DbtTransformationWorker;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.process.KubePodProcess;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.temporal.sync.ReplicationLauncherWorker;
import java.nio.file.Path;
import java.util.Optional;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class DbtJobOrchestrator implements JobOrchestrator<OperatorDbtInput> {

  private final Configs configs;
  private final WorkerConfigs workerConfigs;
  private final ProcessFactory processFactory;

  public DbtJobOrchestrator(final Configs configs, final WorkerConfigs workerConfigs, final ProcessFactory processFactory) {
    this.configs = configs;
    this.workerConfigs = workerConfigs;
    this.processFactory = processFactory;
  }

  @Override
  public String getOrchestratorName() {
    return "DBT Transformation";
  }

  @Override
  public Class<OperatorDbtInput> getInputClass() {
    return OperatorDbtInput.class;
  }

  @Override
  public Optional<String> runJob() throws Exception {
    final JobRunConfig jobRunConfig = JobOrchestrator.readJobRunConfig();
    final OperatorDbtInput dbtInput = readInput();

    final IntegrationLauncherConfig destinationLauncherConfig = JobOrchestrator.readAndDeserializeFile(
        Path.of(KubePodProcess.CONFIG_DIR, ReplicationLauncherWorker.INIT_FILE_DESTINATION_LAUNCHER_CONFIG),
        IntegrationLauncherConfig.class);

    log.info("Setting up dbt worker...");
    final DbtTransformationWorker worker = new DbtTransformationWorker(
        jobRunConfig.getJobId(),
        Math.toIntExact(jobRunConfig.getAttemptId()),
        workerConfigs.getResourceRequirements(),
        new DbtTransformationRunner(
            workerConfigs,
            processFactory, NormalizationRunnerFactory.create(
                workerConfigs,
                destinationLauncherConfig.getDockerImage(),
                processFactory,
                NormalizationRunnerFactory.NORMALIZATION_VERSION)));

    log.info("Running dbt worker...");
    final Path jobRoot = WorkerUtils.getJobRoot(configs.getWorkspaceRoot(), jobRunConfig.getJobId(), jobRunConfig.getAttemptId());
    worker.run(dbtInput, jobRoot);

    return Optional.empty();
  }

}
