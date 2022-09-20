/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.config;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.AirbyteConfigValidator;
import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.Configs.SecretPersistenceType;
import io.airbyte.config.Configs.TrackingStrategy;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.Configs.WorkerPlane;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.metrics.lib.MetricClient;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.scheduler.persistence.DefaultJobCreator;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WebUrlHelper;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.workers.WorkerConfigs;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.micronaut.core.util.StringUtils;
import java.nio.file.Path;
import java.time.Instant;
import java.util.Locale;
import java.util.function.Function;
import java.util.function.Supplier;
import javax.inject.Named;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

/**
 * Micronaut bean factory for general singletons.
 */
@Factory
@Slf4j
@SuppressWarnings("PMD.AvoidDuplicateLiterals")
public class ApplicationBeanFactory {

  @Singleton
  public AirbyteVersion airbyteVersion(@Value("${airbyte.version}") final String airbyteVersion) {
    return new AirbyteVersion(airbyteVersion);
  }

  @Singleton
  public DeploymentMode deploymentMode(@Value("${airbyte.deployment-mode}") final String deploymentMode) {
    return convertToEnum(deploymentMode, DeploymentMode::valueOf, DeploymentMode.OSS);
  }

  @Singleton
  public SecretPersistenceType secretPersistenceType(@Value("${airbyte.secret.persistence}") final String secretPersistence) {
    return convertToEnum(secretPersistence, SecretPersistenceType::valueOf,
        SecretPersistenceType.TESTING_CONFIG_DB_TABLE);
  }

  @Singleton
  public TrackingStrategy trackingStrategy(@Value("${airbyte.tracking-strategy}") final String trackingStrategy) {
    return convertToEnum(trackingStrategy, TrackingStrategy::valueOf, TrackingStrategy.LOGGING);
  }

  @Singleton
  public WorkerEnvironment workerEnvironment(@Value("${airbyte.worker.env}") final String workerEnv) {
    return convertToEnum(workerEnv, WorkerEnvironment::valueOf, WorkerEnvironment.DOCKER);
  }

  @Singleton
  public WorkerPlane workerPlane(@Value("${airbyte.worker.plane}") final String workerPlane) {
    return convertToEnum(workerPlane, WorkerPlane::valueOf, WorkerPlane.CONTROL_PLANE);
  }

  @Singleton
  @Named("workspaceRoot")
  public Path workspaceRoot(@Value("${airbyte.workspace.root}") final String workspaceRoot) {
    return Path.of(workspaceRoot);
  }

  @Singleton
  @Named("currentSecondsSupplier")
  public Supplier<Long> currentSecondsSupplier() {
    return () -> Instant.now().getEpochSecond();
  }

  @Singleton
  public DefaultJobCreator defaultJobCreator(final JobPersistence jobPersistence,
                                             @Named("defaultWorkerConfigs") final WorkerConfigs defaultWorkerConfigs,
                                             final StatePersistence statePersistence) {
    return new DefaultJobCreator(
        jobPersistence,
        defaultWorkerConfigs.getResourceRequirements(),
        statePersistence);
  }

  @Singleton
  public FeatureFlags featureFlags() {
    return new EnvVariableFeatureFlags();
  }

  @Singleton
  @Requires(property = "airbyte.worker.plane",
            pattern = "(?i)^(?!data_plane).*")
  public JobNotifier jobNotifier(
                                 final ConfigRepository configRepository,
                                 final TrackingClient trackingClient,
                                 final WebUrlHelper webUrlHelper,
                                 final WorkspaceHelper workspaceHelper) {
    return new JobNotifier(
        webUrlHelper,
        configRepository,
        workspaceHelper,
        trackingClient);
  }

  @Singleton
  @Requires(property = "airbyte.worker.plane",
            pattern = "(?i)^(?!data_plane).*")
  public JobTracker jobTracker(
                               final ConfigRepository configRepository,
                               final JobPersistence jobPersistence,
                               final TrackingClient trackingClient) {
    return new JobTracker(configRepository, jobPersistence, trackingClient);
  }

  @Singleton
  @Requires(property = "airbyte.worker.plane",
            pattern = "(?i)^(?!data_plane).*")
  public JsonSecretsProcessor jsonSecretsProcessor(final FeatureFlags featureFlags) {
    return JsonSecretsProcessor.builder()
        .maskSecrets(!featureFlags.exposeSecretsInExport())
        .copySecrets(false)
        .build();
  }

  @Singleton
  @Requires(property = "airbyte.worker.plane",
            pattern = "(?i)^(?!data_plane).*")
  public WebUrlHelper webUrlHelper(@Value("${airbyte.web-app.url}") final String webAppUrl) {
    return new WebUrlHelper(webAppUrl);
  }

  @Singleton
  @Requires(property = "airbyte.worker.plane",
            pattern = "(?i)^(?!data_plane).*")
  public WorkspaceHelper workspaceHelper(
                                         final ConfigRepository configRepository,
                                         final JobPersistence jobPersistence) {
    return new WorkspaceHelper(
        configRepository,
        jobPersistence);
  }

  @Singleton
  public AirbyteConfigValidator airbyteConfigValidator() {
    return new AirbyteConfigValidator();
  };

  @Singleton
  public MetricClient metricClient() {
    return MetricClientFactory.getMetricClient();
  }

  private <T> T convertToEnum(final String value, final Function<String, T> creatorFunction, final T defaultValue) {
    return StringUtils.isNotEmpty(value) ? creatorFunction.apply(value.toUpperCase(Locale.ROOT)) : defaultValue;
  }

}
