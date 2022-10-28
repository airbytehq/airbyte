/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import static io.airbyte.metrics.lib.ApmTraceConstants.JOB_ORCHESTRATOR_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.DESTINATION_DOCKER_IMAGE_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;

import datadog.trace.api.Trace;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.config.Configs;
import io.airbyte.config.OperatorDbtInput;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.general.DbtTransformationRunner;
import io.airbyte.workers.general.DbtTransformationWorker;
import io.airbyte.workers.normalization.NormalizationRunnerFactory;
import io.airbyte.workers.process.KubePodProcess;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.sync.ReplicationLauncherWorker;
import java.nio.file.Path;
import java.util.Map;
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

  @Trace(operationName = JOB_ORCHESTRATOR_OPERATION_NAME)
  @Override
  public Optional<String> runJob() throws Exception {
    final JobRunConfig jobRunConfig = JobOrchestrator.readJobRunConfig();
    final OperatorDbtInput dbtInput = readInput();

    final IntegrationLauncherConfig destinationLauncherConfig = JobOrchestrator.readAndDeserializeFile(
        Path.of(KubePodProcess.CONFIG_DIR, ReplicationLauncherWorker.INIT_FILE_DESTINATION_LAUNCHER_CONFIG),
        IntegrationLauncherConfig.class);

    ApmTraceUtils
        .addTagsToTrace(Map.of(JOB_ID_KEY, jobRunConfig.getJobId(), DESTINATION_DOCKER_IMAGE_KEY, destinationLauncherConfig.getDockerImage()));

    log.info("Setting up dbt worker...");
    final DbtTransformationWorker worker = new DbtTransformationWorker(
        jobRunConfig.getJobId(),
        Math.toIntExact(jobRunConfig.getAttemptId()),
        workerConfigs.getResourceRequirements(),
        new DbtTransformationRunner(
            processFactory, NormalizationRunnerFactory.create(
                destinationLauncherConfig.getDockerImage(),
                processFactory,
                NormalizationRunnerFactory.NORMALIZATION_VERSION)));

    log.info("Running dbt worker...");
    final Path jobRoot = TemporalUtils.getJobRoot(configs.getWorkspaceRoot(), jobRunConfig.getJobId(), jobRunConfig.getAttemptId());
    worker.run(dbtInput, jobRoot);

    return Optional.empty();
  }

}
