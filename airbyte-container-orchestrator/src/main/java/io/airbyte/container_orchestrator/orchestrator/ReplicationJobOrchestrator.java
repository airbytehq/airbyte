/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator.orchestrator;

import static io.airbyte.metrics.lib.ApmTraceConstants.JOB_ORCHESTRATOR_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.DESTINATION_DOCKER_IMAGE_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.SOURCE_DOCKER_IMAGE_KEY;

import datadog.trace.api.Trace;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.protocol.AirbyteMessageSerDeProvider;
import io.airbyte.commons.protocol.AirbyteMessageVersionedMigratorFactory;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.config.Configs;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.workers.general.DefaultReplicationWorkerFactory;
import io.airbyte.workers.process.KubePodProcess;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.sync.ReplicationLauncherWorker;
import java.lang.invoke.MethodHandles;
import java.nio.file.Path;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ReplicationJobOrchestrator implements JobOrchestrator<StandardSyncInput> {

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());
  private final ProcessFactory processFactory;
  private final Configs configs;
  private final FeatureFlags featureFlags;
  private final AirbyteMessageSerDeProvider serDeProvider;
  private final AirbyteMessageVersionedMigratorFactory migratorFactory;
  private final JobRunConfig jobRunConfig;

  public ReplicationJobOrchestrator(final Configs configs,
                                    final ProcessFactory processFactory,
                                    final FeatureFlags featureFlags,
                                    final AirbyteMessageSerDeProvider serDeProvider,
                                    final AirbyteMessageVersionedMigratorFactory migratorFactory,
                                    final JobRunConfig jobRunConfig) {
    this.configs = configs;
    this.processFactory = processFactory;
    this.featureFlags = featureFlags;
    this.serDeProvider = serDeProvider;
    this.migratorFactory = migratorFactory;
    this.jobRunConfig = jobRunConfig;
  }

  @Override
  public String getOrchestratorName() {
    return "Replication";
  }

  @Override
  public Class<StandardSyncInput> getInputClass() {
    return StandardSyncInput.class;
  }

  @Trace(operationName = JOB_ORCHESTRATOR_OPERATION_NAME)
  @Override
  public Optional<String> runJob() throws Exception {
    final var syncInput = readInput();

    final var sourceLauncherConfig = JobOrchestrator.readAndDeserializeFile(
        Path.of(KubePodProcess.CONFIG_DIR, ReplicationLauncherWorker.INIT_FILE_SOURCE_LAUNCHER_CONFIG),
        IntegrationLauncherConfig.class);

    final var destinationLauncherConfig = JobOrchestrator.readAndDeserializeFile(
        Path.of(KubePodProcess.CONFIG_DIR, ReplicationLauncherWorker.INIT_FILE_DESTINATION_LAUNCHER_CONFIG),
        IntegrationLauncherConfig.class);
    log.info("sourceLauncherConfig is: " + sourceLauncherConfig.toString());
    log.info("destinationLauncherConfig is: " + destinationLauncherConfig.toString());

    ApmTraceUtils.addTagsToTrace(
        Map.of(JOB_ID_KEY, jobRunConfig.getJobId(),
            DESTINATION_DOCKER_IMAGE_KEY, destinationLauncherConfig.getDockerImage(),
            SOURCE_DOCKER_IMAGE_KEY, sourceLauncherConfig.getDockerImage()));

    // At this moment, if either source or destination is from custom connector image, we will put all
    // jobs into isolated pool to run.
    final boolean useIsolatedPool = sourceLauncherConfig.getIsCustomConnector() || destinationLauncherConfig.getIsCustomConnector();

    log.info("Setting up replication worker...");
    final var replicationWorker = DefaultReplicationWorkerFactory.create(
        jobRunConfig.getJobId(),
        Math.toIntExact(jobRunConfig.getAttemptId()),
        processFactory,
        sourceLauncherConfig.getDockerImage(),
        destinationLauncherConfig.getDockerImage(),
        useIsolatedPool,
        useIsolatedPool,
        sourceLauncherConfig.getProtocolVersion(),
        destinationLauncherConfig.getProtocolVersion(),
        syncInput,
        serDeProvider,
        migratorFactory,
        featureFlags,
        featureFlags.applyFieldSelection());

    log.info("Running replication worker...");
    final var jobRoot = TemporalUtils.getJobRoot(
        configs.getWorkspaceRoot(),
        jobRunConfig.getJobId(),
        jobRunConfig.getAttemptId());
    final ReplicationOutput replicationOutput = replicationWorker.run(syncInput, jobRoot);

    log.info("Returning output...");
    return Optional.of(Jsons.serialize(replicationOutput));
  }

}
