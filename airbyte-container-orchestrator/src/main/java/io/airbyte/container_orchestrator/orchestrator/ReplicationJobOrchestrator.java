/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.container_orchestrator.orchestrator;

import static io.airbyte.metrics.lib.ApmTraceConstants.JOB_ORCHESTRATOR_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.DESTINATION_DOCKER_IMAGE_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.JOB_ID_KEY;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.SOURCE_DOCKER_IMAGE_KEY;

import datadog.trace.api.Trace;
import io.airbyte.api.client.generated.DestinationApi;
import io.airbyte.api.client.generated.SourceApi;
import io.airbyte.commons.features.FeatureFlagHelper;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.commons.protocol.AirbyteMessageSerDeProvider;
import io.airbyte.commons.protocol.AirbyteProtocolVersionedMigratorFactory;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.commons.version.Version;
import io.airbyte.config.Configs;
import io.airbyte.config.ReplicationOutput;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.featureflag.FeatureFlagClient;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.metrics.lib.MetricEmittingApps;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.RecordSchemaValidator;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerMetricReporter;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.general.DefaultReplicationWorker;
import io.airbyte.workers.helper.ConnectorConfigUpdater;
import io.airbyte.workers.internal.AirbyteStreamFactory;
import io.airbyte.workers.internal.DefaultAirbyteDestination;
import io.airbyte.workers.internal.DefaultAirbyteSource;
import io.airbyte.workers.internal.DefaultAirbyteStreamFactory;
import io.airbyte.workers.internal.EmptyAirbyteSource;
import io.airbyte.workers.internal.NamespacingMapper;
import io.airbyte.workers.internal.VersionedAirbyteMessageBufferedWriterFactory;
import io.airbyte.workers.internal.VersionedAirbyteStreamFactory;
import io.airbyte.workers.internal.book_keeping.AirbyteMessageTracker;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
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
  private final FeatureFlagClient featureFlagClient;
  private final AirbyteMessageSerDeProvider serDeProvider;
  private final AirbyteProtocolVersionedMigratorFactory migratorFactory;
  private final JobRunConfig jobRunConfig;
  private final SourceApi sourceApi;
  private final DestinationApi destinationApi;

  public ReplicationJobOrchestrator(final Configs configs,
                                    final ProcessFactory processFactory,
                                    final FeatureFlags featureFlags,
                                    final FeatureFlagClient featureFlagClient,
                                    final AirbyteMessageSerDeProvider serDeProvider,
                                    final AirbyteProtocolVersionedMigratorFactory migratorFactory,
                                    final JobRunConfig jobRunConfig,
                                    final SourceApi sourceApi,
                                    final DestinationApi destinationApi) {
    this.configs = configs;
    this.processFactory = processFactory;
    this.featureFlags = featureFlags;
    this.featureFlagClient = featureFlagClient;
    this.serDeProvider = serDeProvider;
    this.migratorFactory = migratorFactory;
    this.jobRunConfig = jobRunConfig;
    this.sourceApi = sourceApi;
    this.destinationApi = destinationApi;
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

    ApmTraceUtils.addTagsToTrace(
        Map.of(JOB_ID_KEY, jobRunConfig.getJobId(),
            DESTINATION_DOCKER_IMAGE_KEY, destinationLauncherConfig.getDockerImage(),
            SOURCE_DOCKER_IMAGE_KEY, sourceLauncherConfig.getDockerImage()));

    // At this moment, if either source or destination is from custom connector image, we will put all
    // jobs into isolated pool to run.
    final boolean useIsolatedPool = sourceLauncherConfig.getIsCustomConnector() || destinationLauncherConfig.getIsCustomConnector();
    log.info("Setting up source launcher...");
    final var sourceLauncher = new AirbyteIntegrationLauncher(
        sourceLauncherConfig.getJobId(),
        Math.toIntExact(sourceLauncherConfig.getAttemptId()),
        sourceLauncherConfig.getDockerImage(),
        processFactory,
        syncInput.getSourceResourceRequirements(),
        sourceLauncherConfig.getAllowedHosts(),
        useIsolatedPool,
        featureFlags);

    log.info("Setting up destination launcher...");
    final var destinationLauncher = new AirbyteIntegrationLauncher(
        destinationLauncherConfig.getJobId(),
        Math.toIntExact(destinationLauncherConfig.getAttemptId()),
        destinationLauncherConfig.getDockerImage(),
        processFactory,
        syncInput.getDestinationResourceRequirements(),
        destinationLauncherConfig.getAllowedHosts(),
        useIsolatedPool,
        featureFlags);

    log.info("Setting up source...");
    // reset jobs use an empty source to induce resetting all data in destination.
    final var airbyteSource =
        WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB.equals(sourceLauncherConfig.getDockerImage()) ? new EmptyAirbyteSource(
            featureFlags.useStreamCapableState())
            : new DefaultAirbyteSource(sourceLauncher,
                getStreamFactory(sourceLauncherConfig.getProtocolVersion(), syncInput.getCatalog(), DefaultAirbyteSource.CONTAINER_LOG_MDC_BUILDER),
                migratorFactory.getProtocolSerializer(sourceLauncherConfig.getProtocolVersion()), featureFlags);

    MetricClientFactory.initialize(MetricEmittingApps.WORKER);
    final var metricClient = MetricClientFactory.getMetricClient();
    final var metricReporter = new WorkerMetricReporter(metricClient,
        sourceLauncherConfig.getDockerImage());

    log.info("Setting up replication worker...");
    final var replicationWorker = new DefaultReplicationWorker(
        jobRunConfig.getJobId(),
        Math.toIntExact(jobRunConfig.getAttemptId()),
        airbyteSource,
        new NamespacingMapper(syncInput.getNamespaceDefinition(), syncInput.getNamespaceFormat(), syncInput.getPrefix()),
        new DefaultAirbyteDestination(destinationLauncher,
            getStreamFactory(destinationLauncherConfig.getProtocolVersion(), syncInput.getCatalog(),
                DefaultAirbyteDestination.CONTAINER_LOG_MDC_BUILDER),
            new VersionedAirbyteMessageBufferedWriterFactory(serDeProvider, migratorFactory, destinationLauncherConfig.getProtocolVersion(),
                Optional.of(syncInput.getCatalog())),
            migratorFactory.getProtocolSerializer(destinationLauncherConfig.getProtocolVersion())),
        new AirbyteMessageTracker(featureFlags),
        new RecordSchemaValidator(featureFlagClient, syncInput.getWorkspaceId(), WorkerUtils.mapStreamNamesToSchemas(syncInput)),
        metricReporter,
        new ConnectorConfigUpdater(sourceApi, destinationApi),
        FeatureFlagHelper.isFieldSelectionEnabledForWorkspace(featureFlags, syncInput.getWorkspaceId()));

    log.info("Running replication worker...");
    final var jobRoot = TemporalUtils.getJobRoot(configs.getWorkspaceRoot(),
        jobRunConfig.getJobId(), jobRunConfig.getAttemptId());
    final ReplicationOutput replicationOutput = replicationWorker.run(syncInput, jobRoot);

    log.info("Returning output...");
    return Optional.of(Jsons.serialize(replicationOutput));
  }

  private AirbyteStreamFactory getStreamFactory(final Version protocolVersion,
                                                final ConfiguredAirbyteCatalog configuredAirbyteCatalog,
                                                final MdcScope.Builder mdcScope) {
    return protocolVersion != null
        ? new VersionedAirbyteStreamFactory<>(serDeProvider, migratorFactory, protocolVersion, Optional.of(configuredAirbyteCatalog), mdcScope,
            Optional.of(RuntimeException.class))
        : new DefaultAirbyteStreamFactory(mdcScope);
  }

}
