/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.Configs;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.metrics.lib.MetricClient;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.metrics.lib.MetricEmittingApps;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.commons.worker.RecordSchemaValidator;
import io.airbyte.commons.worker.WorkerConstants;
import io.airbyte.commons.worker.WorkerMetricReporter;
import io.airbyte.commons.worker.WorkerUtils;
import io.airbyte.commons.worker.general.DefaultReplicationWorker;
import io.airbyte.commons.worker.general.ReplicationWorker;
import io.airbyte.commons.worker.internal.AirbyteMessageTracker;
import io.airbyte.commons.worker.internal.AirbyteSource;
import io.airbyte.commons.worker.internal.DefaultAirbyteDestination;
import io.airbyte.commons.worker.internal.DefaultAirbyteSource;
import io.airbyte.commons.worker.internal.EmptyAirbyteSource;
import io.airbyte.commons.worker.internal.NamespacingMapper;
import io.airbyte.commons.worker.process.AirbyteIntegrationLauncher;
import io.airbyte.commons.worker.process.IntegrationLauncher;
import io.airbyte.commons.worker.process.KubePodProcess;
import io.airbyte.commons.worker.process.ProcessFactory;
import io.airbyte.commons.worker.sync.ReplicationLauncherWorker;
import java.nio.file.Path;
import java.util.Optional;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class ReplicationJobOrchestrator implements JobOrchestrator<StandardSyncInput> {

  private final ProcessFactory processFactory;
  private final Configs configs;
  private final FeatureFlags featureFlags;

  public ReplicationJobOrchestrator(final Configs configs,
                                    final ProcessFactory processFactory,
                                    final FeatureFlags featureFlags) {
    this.configs = configs;
    this.processFactory = processFactory;
    this.featureFlags = featureFlags;
  }

  @Override
  public String getOrchestratorName() {
    return "Replication";
  }

  @Override
  public Class<StandardSyncInput> getInputClass() {
    return StandardSyncInput.class;
  }

  @Override
  public Optional<String> runJob() throws Exception {
    final JobRunConfig jobRunConfig = JobOrchestrator.readJobRunConfig();
    final StandardSyncInput syncInput = readInput();

    final IntegrationLauncherConfig sourceLauncherConfig = JobOrchestrator.readAndDeserializeFile(
        Path.of(KubePodProcess.CONFIG_DIR, ReplicationLauncherWorker.INIT_FILE_SOURCE_LAUNCHER_CONFIG),
        IntegrationLauncherConfig.class);

    final IntegrationLauncherConfig destinationLauncherConfig = JobOrchestrator.readAndDeserializeFile(
        Path.of(KubePodProcess.CONFIG_DIR, ReplicationLauncherWorker.INIT_FILE_DESTINATION_LAUNCHER_CONFIG),
        IntegrationLauncherConfig.class);

    log.info("Setting up source launcher...");
    final IntegrationLauncher sourceLauncher = new AirbyteIntegrationLauncher(
        sourceLauncherConfig.getJobId(),
        Math.toIntExact(sourceLauncherConfig.getAttemptId()),
        sourceLauncherConfig.getDockerImage(),
        processFactory,
        syncInput.getSourceResourceRequirements());

    log.info("Setting up destination launcher...");
    final IntegrationLauncher destinationLauncher = new AirbyteIntegrationLauncher(
        destinationLauncherConfig.getJobId(),
        Math.toIntExact(destinationLauncherConfig.getAttemptId()),
        destinationLauncherConfig.getDockerImage(),
        processFactory,
        syncInput.getDestinationResourceRequirements());

    log.info("Setting up source...");
    // reset jobs use an empty source to induce resetting all data in destination.
    final AirbyteSource airbyteSource =
        WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB.equals(sourceLauncherConfig.getDockerImage()) ? new EmptyAirbyteSource(
            featureFlags.useStreamCapableState())
            : new DefaultAirbyteSource(sourceLauncher);

    MetricClientFactory.initialize(MetricEmittingApps.WORKER);
    final MetricClient metricClient = MetricClientFactory.getMetricClient();
    final WorkerMetricReporter metricReporter = new WorkerMetricReporter(metricClient, sourceLauncherConfig.getDockerImage());

    log.info("Setting up replication worker...");
    final ReplicationWorker replicationWorker = new DefaultReplicationWorker(
        jobRunConfig.getJobId(),
        Math.toIntExact(jobRunConfig.getAttemptId()),
        airbyteSource,
        new NamespacingMapper(syncInput.getNamespaceDefinition(), syncInput.getNamespaceFormat(), syncInput.getPrefix()),
        new DefaultAirbyteDestination(destinationLauncher),
        new AirbyteMessageTracker(),
        new RecordSchemaValidator(WorkerUtils.mapStreamNamesToSchemas(syncInput)),
        metricReporter);

    log.info("Running replication worker...");
    final Path jobRoot = WorkerUtils.getJobRoot(configs.getWorkspaceRoot(), jobRunConfig.getJobId(), jobRunConfig.getAttemptId());
    final ReplicationOutput replicationOutput = replicationWorker.run(syncInput, jobRoot);

    log.info("Returning output...");
    return Optional.of(Jsons.serialize(replicationOutput));
  }

}
