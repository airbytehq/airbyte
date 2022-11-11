/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.config;

import io.airbyte.analytics.Deployment;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.temporal.TemporalClient;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.Configs.TrackingStrategy;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.DefaultJobCreator;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.WorkspaceHelper;
import io.airbyte.persistence.job.factory.DefaultSyncJobFactory;
import io.airbyte.persistence.job.factory.OAuthConfigSupplier;
import io.airbyte.persistence.job.factory.SyncJobFactory;
import io.airbyte.workers.run.TemporalWorkerRunFactory;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Property;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.worker.WorkerFactory;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Optional;

/**
 * Micronaut bean factory for Temporal-related singletons.
 */
@Factory
public class TemporalBeanFactory {

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  public TrackingClient trackingClient(final Optional<TrackingStrategy> trackingStrategy,
                                       final DeploymentMode deploymentMode,
                                       Optional<JobPersistence> jobPersistence,
                                       WorkerEnvironment workerEnvironment,
                                       @Value("${airbyte.role}") String airbyteRole,
                                       AirbyteVersion airbyteVersion,
                                       Optional<ConfigRepository> configRepository)
      throws IOException {

    TrackingClientSingleton.initialize(
        trackingStrategy.orElseThrow(),
        new Deployment(deploymentMode, jobPersistence.orElseThrow().getDeployment().orElseThrow(),
            workerEnvironment),
        airbyteRole,
        airbyteVersion,
        configRepository.orElseThrow());

    return TrackingClientSingleton.get();
  }

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  public SyncJobFactory jobFactory(
                                   final ConfigRepository configRepository,
                                   final JobPersistence jobPersistence,
                                   @Property(name = "airbyte.connector.specific-resource-defaults-enabled",
                                             defaultValue = "false") final boolean connectorSpecificResourceDefaultsEnabled,
                                   final DefaultJobCreator jobCreator,
                                   final TrackingClient trackingClient) {
    return new DefaultSyncJobFactory(
        connectorSpecificResourceDefaultsEnabled,
        jobCreator,
        configRepository,
        new OAuthConfigSupplier(configRepository, trackingClient),
        new WorkspaceHelper(configRepository, jobPersistence));
  }

  @Singleton
  @Requires(env = WorkerMode.CONTROL_PLANE)
  public TemporalWorkerRunFactory temporalWorkerRunFactory(
                                                           @Value("${airbyte.version}") final String airbyteVersion,
                                                           final FeatureFlags featureFlags,
                                                           final TemporalClient temporalClient,
                                                           final TemporalUtils temporalUtils,
                                                           final WorkflowServiceStubs temporalService,
                                                           @Value("${airbyte.workspace.root}") final String workspaceRoot) {
    return new TemporalWorkerRunFactory(
        temporalClient,
        Path.of(workspaceRoot),
        airbyteVersion,
        featureFlags);
  }

  @Singleton
  public WorkerFactory workerFactory(final WorkflowClient workflowClient) {
    return WorkerFactory.newInstance(workflowClient);
  }

}
