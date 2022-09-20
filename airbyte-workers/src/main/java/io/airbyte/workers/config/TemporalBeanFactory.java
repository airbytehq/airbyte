/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.config;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.DefaultJobCreator;
import io.airbyte.scheduler.persistence.job_factory.DefaultSyncJobFactory;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
import io.airbyte.workers.run.TemporalWorkerRunFactory;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalUtils;
import io.airbyte.workers.temporal.TemporalWorkflowUtils;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Property;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.worker.WorkerFactory;
import java.nio.file.Path;
import javax.inject.Singleton;

/**
 * Micronaut bean factory for Temporal-related singletons.
 */
@Factory
public class TemporalBeanFactory {

  @Singleton
  @Requires(property = "airbyte.worker.plane",
            pattern = "(?i)^(?!data_plane).*")
  public TrackingClient trackingClient() {
    return TrackingClientSingleton.get();
  }

  @Singleton
  @Requires(property = "airbyte.worker.plane",
            pattern = "(?i)^(?!data_plane).*")
  public SyncJobFactory jobFactory(
                                   final ConfigRepository configRepository,
                                   @Property(name = "airbyte.connector.specific-resource-defaults-enabled",
                                             defaultValue = "false") final boolean connectorSpecificResourceDefaultsEnabled,
                                   final DefaultJobCreator jobCreator,
                                   final TrackingClient trackingClient) {
    return new DefaultSyncJobFactory(
        connectorSpecificResourceDefaultsEnabled,
        jobCreator,
        configRepository,
        new OAuthConfigSupplier(configRepository, trackingClient));
  }

  @Singleton
  public WorkflowServiceStubs temporalService(final TemporalUtils temporalUtils) {
    return temporalUtils.createTemporalService();
  }

  @Singleton
  public WorkflowClient workflowClient(
                                       final TemporalUtils temporalUtils,
                                       final WorkflowServiceStubs temporalService) {
    return TemporalWorkflowUtils.createWorkflowClient(temporalService, temporalUtils.getNamespace());
  }

  @Singleton
  @Requires(property = "airbyte.worker.plane",
            pattern = "(?i)^(?!data_plane).*")
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
