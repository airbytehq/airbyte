/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.config;

import com.github.slugify.Slugify;
import io.airbyte.analytics.Deployment;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.io.FileTtlManager;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.SecretsRepositoryReader;
import io.airbyte.config.persistence.SecretsRepositoryWriter;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.db.instance.FlywayConfigurationConstants;
import io.airbyte.oauth.OAuthImplementationFactory;
import io.airbyte.scheduler.client.DefaultSchedulerJobClient;
import io.airbyte.scheduler.client.DefaultSynchronousSchedulerClient;
import io.airbyte.scheduler.client.EventRunner;
import io.airbyte.scheduler.client.SchedulerJobClient;
import io.airbyte.scheduler.client.TemporalEventRunner;
import io.airbyte.scheduler.persistence.DefaultJobCreator;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.server.DatabaseInitializer;
import io.airbyte.validation.json.JsonSchemaValidator;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalUtils;
import io.micronaut.context.annotation.Factory;
import io.micronaut.context.annotation.Value;
import io.micronaut.flyway.FlywayConfigurationProperties;
import io.micronaut.http.client.DefaultHttpClientConfiguration;
import io.micronaut.http.client.HttpClient;
import io.micronaut.http.client.HttpClientConfiguration;
import io.micronaut.http.client.netty.DefaultHttpClient;
import io.micronaut.http.uri.UriBuilder;
import io.temporal.serviceclient.WorkflowServiceStubs;
import java.io.IOException;
import java.time.Duration;
import java.util.Optional;
import java.util.UUID;
import java.util.concurrent.TimeUnit;
import java.util.function.Supplier;
import javax.inject.Named;
import javax.inject.Singleton;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;

@Factory
public class ApplicationBeanFactory {

  @Singleton
  public Configs configs() {
    return new EnvConfigs();
  }

  @Singleton
  public WorkerConfigs workerConfigs(final Configs configs) {
    return new WorkerConfigs(configs);
  }

  @Singleton
  public WorkerEnvironment workerEnvironment(final Configs configs) {
    return configs.getWorkerEnvironment();
  }

  @Singleton
  public LogConfigs logConfigs(final Configs configs) {
    return configs.getLogConfigs();
  }

  @Singleton
  public AirbyteVersion airbyteVersion(@Value("${airbyte.version}") final String version) {
    return new AirbyteVersion(version);
  }

  @Singleton
  public LogClientSingleton logClient(final Configs configs) {
    final LogClientSingleton logClient = LogClientSingleton.getInstance();
    logClient.setWorkspaceMdc(
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        LogClientSingleton.getInstance().getServerLogsRoot(configs.getWorkspaceRoot()));
    return logClient;
  }

  @Singleton
  public SecretsHydrator secretsHydrator(final Configs configs, @Named("config") final DSLContext dslContext) throws IOException {
    return SecretPersistence.getSecretsHydrator(configs, dslContext);
  }

  @Singleton
  @Named("secretPersistence")
  public Optional<SecretPersistence> secretPersistence(final Configs configs, @Named("config") final DSLContext dslContext) throws IOException {
    return SecretPersistence.getLongLived(configs, dslContext);
  }

  @Singleton
  @Named("ephemeralSecretPersistence")
  public Optional<SecretPersistence> ephemeralSecretPersistence(final Configs configs, @Named("config") final DSLContext dslContext)
      throws IOException {
    return SecretPersistence.getEphemeral(configs, dslContext);
  }

  @Singleton
  public SecretsRepositoryReader secretsRepositoryReader(final ConfigRepository configRepository, final SecretsHydrator secretsHydrator) {
    return new SecretsRepositoryReader(configRepository, secretsHydrator);
  }

  @Singleton
  public SecretsRepositoryWriter secretsRepositoryWriter(final ConfigRepository configRepository,
                                                         @Named("secretPersistence") final Optional<SecretPersistence> secretPersistence,
                                                         @Named("ephemeralSecretPersistence") final Optional<SecretPersistence> ephemeralSecretPersistence) {
    return new SecretsRepositoryWriter(configRepository, secretPersistence, ephemeralSecretPersistence);
  }

  @Singleton
  public FeatureFlags featureFlags() {
    return new EnvVariableFeatureFlags();
  }

  @Singleton
  public JsonSecretsProcessor jsonSecretsProcessor(final FeatureFlags featureFlags) {
    return JsonSecretsProcessor.builder()
        .maskSecrets(!featureFlags.exposeSecretsInExport())
        .copySecrets(false)
        .build();
  }

  @Singleton
  public TrackingClient trackingClient(final Configs configs, final JobPersistence jobPersistence, final ConfigRepository configRepository)
      throws IOException {
    TrackingClientSingleton.initialize(
        configs.getTrackingStrategy(),
        new Deployment(configs.getDeploymentMode(), jobPersistence.getDeployment().orElseThrow(), configs.getWorkerEnvironment()),
        configs.getAirbyteRole(),
        configs.getAirbyteVersion(),
        configRepository);

    return TrackingClientSingleton.get();
  }

  @Singleton
  public JobTracker jobTracker(final ConfigRepository configRepository, final JobPersistence jobPersistence, final TrackingClient trackingClient) {
    return new JobTracker(configRepository, jobPersistence, trackingClient);
  }

  @Singleton
  public WorkflowServiceStubs temporalService(final Configs configs) {
    return TemporalUtils.createTemporalService(configs.getTemporalHost());
  }

  @Singleton
  public TemporalClient temporalClient(final Configs configs) {
    return TemporalClient.production(configs.getTemporalHost(), configs.getWorkspaceRoot(), configs);
  }

  @Singleton
  public OAuthConfigSupplier oAuthConfigSupplier(final ConfigRepository configRepository, final TrackingClient trackingClient) {
    return new OAuthConfigSupplier(configRepository, trackingClient);
  }

  @Singleton
  public SchedulerJobClient schedulerJobClient(final Configs configs,
                                               final ConfigRepository configRepository,
                                               final JobPersistence jobPersistence,
                                               final WorkerConfigs workerConfigs) {
    return new DefaultSchedulerJobClient(
        configs.connectorSpecificResourceDefaultsEnabled(),
        jobPersistence,
        new DefaultJobCreator(jobPersistence, configRepository, workerConfigs.getResourceRequirements()));
  }

  @Singleton
  public DefaultSynchronousSchedulerClient syncSchedulerClient(final TemporalClient temporalClient,
                                                               final JobTracker jobTracker,
                                                               final OAuthConfigSupplier oAuthConfigSupplier) {
    return new DefaultSynchronousSchedulerClient(temporalClient, jobTracker, oAuthConfigSupplier);
  }

  @Singleton
  public EventRunner eventRunner(final Configs configs) {
    return new TemporalEventRunner(
        TemporalClient.production(configs.getTemporalHost(), configs.getWorkspaceRoot(), configs));
  }

  @Singleton
  public FileTtlManager fileTtlManager() {
    return new FileTtlManager(10, TimeUnit.MINUTES, 10);
  }

  @Singleton
  public WorkspaceHelper workspaceHelper(final ConfigRepository configRepository, final JobPersistence jobPersistence) {
    return new WorkspaceHelper(configRepository, jobPersistence);
  }

  @Singleton
  public JsonSchemaValidator jsonSchemaValidator() {
    return new JsonSchemaValidator();
  }

  @Singleton
  public Supplier<UUID> uuidGenerator() {
    return UUID::randomUUID;
  }

  @Singleton
  public Slugify slugify() {
    return new Slugify();
  }

  @Singleton
  @Named("githubHttpClient")
  public HttpClient githubHttpClient(@Value("${github.base_url}") final String baseUrl, @Value("${github.timeout_ms}") final Long timeout) {
    final Duration timeoutDuration = Duration.ofMillis(timeout);
    final HttpClientConfiguration configuration = new DefaultHttpClientConfiguration();
    configuration.setConnectTimeout(timeoutDuration);
    configuration.setReadTimeout(timeoutDuration);
    return new DefaultHttpClient(UriBuilder.of(baseUrl).build(), configuration);
  }

  @Singleton
  public OAuthImplementationFactory oAuthImplementationFactory(final ConfigRepository configRepository) {
    return new OAuthImplementationFactory(configRepository,
        java.net.http.HttpClient.newBuilder().version(java.net.http.HttpClient.Version.HTTP_1_1).build());
  }

  @Singleton
  public JobNotifier jobNotifier(@Value("${airbyte.web_app_url}") final String webappUrl,
                                 final ConfigRepository configRepository,
                                 final WorkspaceHelper workspaceHelper,
                                 final TrackingClient trackingClient) {
    System.out.println("webappUrl -> " + webappUrl);
    return new JobNotifier(webappUrl, configRepository, workspaceHelper, trackingClient);
  }

  @Singleton
  @Named("configFlyway")
  public Flyway configFlyway(@Named("config") final DataSource configDataSource,
                             @Named("config") final FlywayConfigurationProperties configsFlywayConfigurationProperties) {
    return configsFlywayConfigurationProperties.getFluentConfiguration()
        .dataSource(configDataSource)
        .baselineVersion(FlywayConfigurationConstants.BASELINE_VERSION)
        .baselineDescription(FlywayConfigurationConstants.BASELINE_DESCRIPTION)
        .baselineOnMigrate(FlywayConfigurationConstants.BASELINE_ON_MIGRATION)
        .installedBy(DatabaseInitializer.class.getSimpleName())
        .table(String.format("airbyte_%s_migrations", "configs"))
        .load();
  }

  @Singleton
  @Named("jobsFlyway")
  public Flyway jobsFlyway(@Named("jobs") final DataSource jobsDataSource,
                           @Named("jobs") final FlywayConfigurationProperties jobsFlywayConfigurationProperties) {
    return jobsFlywayConfigurationProperties.getFluentConfiguration()
        .dataSource(jobsDataSource)
        .baselineVersion(FlywayConfigurationConstants.BASELINE_VERSION)
        .baselineDescription(FlywayConfigurationConstants.BASELINE_DESCRIPTION)
        .baselineOnMigrate(FlywayConfigurationConstants.BASELINE_ON_MIGRATION)
        .installedBy(DatabaseInitializer.class.getSimpleName())
        .table(String.format("airbyte_%s_migrations", "jobs"))
        .load();
  }

}
