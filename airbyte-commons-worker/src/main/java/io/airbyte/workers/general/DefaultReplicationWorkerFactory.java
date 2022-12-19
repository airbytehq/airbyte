/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.general;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.logging.MdcScope;
import io.airbyte.commons.protocol.AirbyteMessageSerDeProvider;
import io.airbyte.commons.protocol.AirbyteMessageVersionedMigratorFactory;
import io.airbyte.commons.version.Version;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.metrics.lib.MetricEmittingApps;
import io.airbyte.workers.RecordSchemaValidator;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.WorkerMetricReporter;
import io.airbyte.workers.WorkerUtils;
import io.airbyte.workers.internal.AirbyteSource;
import io.airbyte.workers.internal.AirbyteStreamFactory;
import io.airbyte.workers.internal.DefaultAirbyteDestination;
import io.airbyte.workers.internal.DefaultAirbyteSource;
import io.airbyte.workers.internal.DefaultAirbyteStreamFactory;
import io.airbyte.workers.internal.EmptyAirbyteSource;
import io.airbyte.workers.internal.HeartbeatMonitor;
import io.airbyte.workers.internal.HeartbeatTimeoutChaperone;
import io.airbyte.workers.internal.NamespacingMapper;
import io.airbyte.workers.internal.VersionedAirbyteMessageBufferedWriterFactory;
import io.airbyte.workers.internal.VersionedAirbyteStreamFactory;
import io.airbyte.workers.internal.book_keeping.AirbyteMessageTracker;
import io.airbyte.workers.process.AirbyteIntegrationLauncher;
import io.airbyte.workers.process.IntegrationLauncher;
import io.airbyte.workers.process.ProcessFactory;
import java.lang.invoke.MethodHandles;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultReplicationWorkerFactory {

  private static final Logger log = LoggerFactory.getLogger(MethodHandles.lookup().lookupClass());

  public static DefaultReplicationWorker create(final String jobId,
                                                final int attemptId,
                                                final ProcessFactory processFactory,
                                                final String srcDockerImage,
                                                final String destDockerImage,
                                                final boolean srcIsCustomConnector,
                                                final boolean destIsCustomConnector,
                                                final Version srcProtocolVersion,
                                                final Version destProtocolVersion,
                                                final StandardSyncInput syncInput,
                                                final AirbyteMessageSerDeProvider serdeProvider,
                                                final AirbyteMessageVersionedMigratorFactory migratorFactory,
                                                final FeatureFlags featureFlags,
                                                final boolean fieldSelectionEnabled

  ) {
    log.info("Setting up source launcher...");
    final IntegrationLauncher sourceLauncher = new AirbyteIntegrationLauncher(
        jobId,
        attemptId,
        srcDockerImage,
        processFactory,
        syncInput.getSourceResourceRequirements(),
        srcIsCustomConnector);

    log.info("Setting up destination launcher...");
    final IntegrationLauncher destinationLauncher = new AirbyteIntegrationLauncher(
        jobId,
        attemptId,
        destDockerImage,
        processFactory,
        syncInput.getDestinationResourceRequirements(),
        destIsCustomConnector);

    MetricClientFactory.initialize(MetricEmittingApps.WORKER);
    final var metricClient = MetricClientFactory.getMetricClient();
    final var metricReporter = new WorkerMetricReporter(metricClient, srcDockerImage);

    log.info("Setting up source...");
    // reset jobs use an empty source to induce resetting all data in destination.
    final AirbyteSource airbyteSource;
    if (WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB.equals(srcDockerImage)) {
      airbyteSource = new EmptyAirbyteSource(featureFlags.useStreamCapableState());
    } else {
      airbyteSource = new DefaultAirbyteSource(
          sourceLauncher,
          getStreamFactory(srcProtocolVersion, DefaultAirbyteSource.CONTAINER_LOG_MDC_BUILDER, serdeProvider, migratorFactory));
    }

    log.info("Setting up destination...");
    final var airbyteDestination = new DefaultAirbyteDestination(
        destinationLauncher,
        getStreamFactory(destProtocolVersion, DefaultAirbyteDestination.CONTAINER_LOG_MDC_BUILDER, serdeProvider, migratorFactory),
        new VersionedAirbyteMessageBufferedWriterFactory(serdeProvider, migratorFactory, destProtocolVersion));

    final var srcHeartbeatMonitor = new HeartbeatMonitor(HeartbeatMonitor.DEFAULT_HEARTBEAT_FRESH_DURATION);
    final var srcHeartbeatTimeoutChaperone =
        new HeartbeatTimeoutChaperone(srcHeartbeatMonitor, HeartbeatTimeoutChaperone.DEFAULT_TIMEOUT_CHECK_DURATION);

    log.info("Setting up replication worker...");
    return new DefaultReplicationWorker(
        jobId,
        attemptId,
        airbyteSource,
        new NamespacingMapper(syncInput.getNamespaceDefinition(), syncInput.getNamespaceFormat(), syncInput.getPrefix()),
        airbyteDestination,
        new AirbyteMessageTracker(),
        new RecordSchemaValidator(WorkerUtils.mapStreamNamesToSchemas(syncInput)),
        metricReporter,
        fieldSelectionEnabled,
        srcHeartbeatMonitor,
        srcHeartbeatTimeoutChaperone);
  }

  private static AirbyteStreamFactory getStreamFactory(final Version protocolVersion,
                                                       final MdcScope.Builder mdcScope,
                                                       final AirbyteMessageSerDeProvider serdeProvider,
                                                       final AirbyteMessageVersionedMigratorFactory migratorFactory) {
    return protocolVersion != null
        ? new VersionedAirbyteStreamFactory(serdeProvider, migratorFactory, protocolVersion, mdcScope)
        : new DefaultAirbyteStreamFactory(mdcScope);
  }

}
