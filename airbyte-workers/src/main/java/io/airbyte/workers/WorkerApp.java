/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.analytics.Deployment;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.lang.CloseableShutdownHook;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.MaxWorkersConfig;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.db.Database;
import io.airbyte.db.check.impl.JobsDatabaseAvailabilityCheck;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseCheckFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.factory.FlywayFactory;
import io.airbyte.db.instance.DatabaseConstants;
import io.airbyte.db.instance.configs.ConfigsDatabaseMigrator;
import io.airbyte.db.instance.jobs.JobsDatabaseMigrator;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.metrics.lib.MetricEmittingApps;
import io.airbyte.scheduler.persistence.DefaultJobCreator;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobCreator;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WebUrlHelper;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.scheduler.persistence.job_error_reporter.JobErrorReporter;
import io.airbyte.scheduler.persistence.job_error_reporter.JobErrorReportingClient;
import io.airbyte.scheduler.persistence.job_error_reporter.JobErrorReportingClientFactory;
import io.airbyte.scheduler.persistence.job_factory.DefaultSyncJobFactory;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.workers.general.DocumentStoreClient;
import io.airbyte.workers.helper.ConnectionHelper;
import io.airbyte.workers.process.DockerProcessFactory;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.process.WorkerHeartbeatServer;
import io.airbyte.workers.run.TemporalWorkerRunFactory;
import io.airbyte.workers.storage.StateClients;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalJobType;
import io.airbyte.workers.temporal.TemporalUtils;
import io.airbyte.workers.temporal.check.connection.CheckConnectionActivityImpl;
import io.airbyte.workers.temporal.check.connection.CheckConnectionWorkflowImpl;
import io.airbyte.workers.temporal.discover.catalog.DiscoverCatalogActivityImpl;
import io.airbyte.workers.temporal.discover.catalog.DiscoverCatalogWorkflowImpl;
import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflowImpl;
import io.airbyte.workers.temporal.scheduling.activities.AutoDisableConnectionActivityImpl;
import io.airbyte.workers.temporal.scheduling.activities.ConfigFetchActivityImpl;
import io.airbyte.workers.temporal.scheduling.activities.ConnectionDeletionActivityImpl;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivityImpl;
import io.airbyte.workers.temporal.scheduling.activities.JobCreationAndStatusUpdateActivityImpl;
import io.airbyte.workers.temporal.scheduling.activities.StreamResetActivityImpl;
import io.airbyte.workers.temporal.spec.SpecActivityImpl;
import io.airbyte.workers.temporal.spec.SpecWorkflowImpl;
import io.airbyte.workers.temporal.sync.DbtTransformationActivityImpl;
import io.airbyte.workers.temporal.sync.NormalizationActivityImpl;
import io.airbyte.workers.temporal.sync.PersistStateActivityImpl;
import io.airbyte.workers.temporal.sync.ReplicationActivityImpl;
import io.airbyte.workers.temporal.sync.SyncWorkflowImpl;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import io.temporal.client.WorkflowClient;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.worker.Worker;
import io.temporal.worker.WorkerFactory;
import io.temporal.worker.WorkerOptions;
import java.io.IOException;
import java.net.InetAddress;
import java.nio.file.Path;
import java.time.Instant;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Executors;
import javax.sql.DataSource;
import lombok.AllArgsConstructor;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

@AllArgsConstructor
@SuppressWarnings("PMD.AvoidCatchingThrowable")
public class WorkerApp {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerApp.class);
  public static final int KUBE_HEARTBEAT_PORT = 9000;
  private static final String DRIVER_CLASS_NAME = DatabaseDriver.POSTGRESQL.getDriverClassName();

  // IMPORTANT: Changing the storage location will orphan already existing kube pods when the new
  // version is deployed!
  public static final Path STATE_STORAGE_PREFIX = Path.of("/state");

  private final Path workspaceRoot;
  private final ProcessFactory defaultProcessFactory;
  private final ProcessFactory specProcessFactory;
  private final ProcessFactory checkProcessFactory;
  private final ProcessFactory discoverProcessFactory;
  private final ProcessFactory replicationProcessFactory;
  private final SecretsHydrator secretsHydrator;
  private final WorkflowClient workflowClient;
  private final ConfigRepository configRepository;
  private final MaxWorkersConfig maxWorkers;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final WorkerConfigs defaultWorkerConfigs;
  private final WorkerConfigs specWorkerConfigs;
  private final WorkerConfigs checkWorkerConfigs;
  private final WorkerConfigs discoverWorkerConfigs;
  private final WorkerConfigs replicationWorkerConfigs;
  private final String airbyteVersion;
  private final SyncJobFactory jobFactory;
  private final JobPersistence jobPersistence;
  private final TemporalWorkerRunFactory temporalWorkerRunFactory;
  private final Configs configs;
  private final ConnectionHelper connectionHelper;
  private final Optional<ContainerOrchestratorConfig> containerOrchestratorConfig;
  private final JobNotifier jobNotifier;
  private final JobTracker jobTracker;
  private final JobErrorReporter jobErrorReporter;
  private final StreamResetPersistence streamResetPersistence;
  private final FeatureFlags featureFlags;
  private final JobCreator jobCreator;
  private final StatePersistence statePersistence;

  public void start() {
    final Map<String, String> mdc = MDC.getCopyOfContextMap();
    Executors.newSingleThreadExecutor().submit(
        () -> {
          MDC.setContextMap(mdc);
          try {
            new WorkerHeartbeatServer(KUBE_HEARTBEAT_PORT).start();
          } catch (final Exception e) {
            throw new RuntimeException(e);
          }
        });

    final WorkerFactory factory = WorkerFactory.newInstance(workflowClient);

    if (configs.shouldRunGetSpecWorkflows()) {
      registerGetSpec(factory);
    }

    if (configs.shouldRunCheckConnectionWorkflows()) {
      registerCheckConnection(factory);
    }

    if (configs.shouldRunDiscoverWorkflows()) {
      registerDiscover(factory);
    }

    if (configs.shouldRunSyncWorkflows()) {
      registerSync(factory);
    }

    if (configs.shouldRunConnectionManagerWorkflows()) {
      registerConnectionManager(factory);
    }

    factory.start();
  }

  private void registerConnectionManager(final WorkerFactory factory) {
    final FeatureFlags featureFlags = new EnvVariableFeatureFlags();

    final Worker connectionUpdaterWorker =
        factory.newWorker(TemporalJobType.CONNECTION_UPDATER.toString(), getWorkerOptions(maxWorkers.getMaxSyncWorkers()));
    connectionUpdaterWorker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class);
    connectionUpdaterWorker.registerActivitiesImplementations(
        new GenerateInputActivityImpl(
            jobPersistence),
        new JobCreationAndStatusUpdateActivityImpl(
            jobFactory,
            jobPersistence,
            temporalWorkerRunFactory,
            workerEnvironment,
            logConfigs,
            jobNotifier,
            jobTracker,
            configRepository,
            jobCreator,
            streamResetPersistence,
            jobErrorReporter),
        new ConfigFetchActivityImpl(configRepository, jobPersistence, configs, () -> Instant.now().getEpochSecond()),
        new ConnectionDeletionActivityImpl(connectionHelper),
        new CheckConnectionActivityImpl(
            checkWorkerConfigs,
            checkProcessFactory,
            secretsHydrator,
            workspaceRoot,
            workerEnvironment,
            logConfigs,
            jobPersistence,
            airbyteVersion),
        new AutoDisableConnectionActivityImpl(configRepository, jobPersistence, featureFlags, configs, jobNotifier),
        new StreamResetActivityImpl(streamResetPersistence, jobPersistence));
  }

  private void registerSync(final WorkerFactory factory) {
    final ReplicationActivityImpl replicationActivity = getReplicationActivityImpl(replicationWorkerConfigs, replicationProcessFactory);

    // Note that the configuration injected here is for the normalization orchestrator, and not the
    // normalization pod itself.
    // Configuration for the normalization pod is injected via the SyncWorkflowImpl.
    final NormalizationActivityImpl normalizationActivity = getNormalizationActivityImpl(defaultWorkerConfigs, defaultProcessFactory);

    final DbtTransformationActivityImpl dbtTransformationActivity = getDbtActivityImpl(
        defaultWorkerConfigs,
        defaultProcessFactory);

    final PersistStateActivityImpl persistStateActivity = new PersistStateActivityImpl(statePersistence, featureFlags);

    final Worker syncWorker = factory.newWorker(TemporalJobType.SYNC.name(), getWorkerOptions(maxWorkers.getMaxSyncWorkers()));

    syncWorker.registerWorkflowImplementationTypes(SyncWorkflowImpl.class);
    syncWorker.registerActivitiesImplementations(replicationActivity, normalizationActivity, dbtTransformationActivity, persistStateActivity);

  }

  private void registerDiscover(final WorkerFactory factory) {
    final Worker discoverWorker = factory.newWorker(TemporalJobType.DISCOVER_SCHEMA.name(), getWorkerOptions(maxWorkers.getMaxDiscoverWorkers()));
    discoverWorker.registerWorkflowImplementationTypes(DiscoverCatalogWorkflowImpl.class);
    discoverWorker
        .registerActivitiesImplementations(
            new DiscoverCatalogActivityImpl(discoverWorkerConfigs, discoverProcessFactory, secretsHydrator, workspaceRoot, workerEnvironment,
                logConfigs,
                jobPersistence, airbyteVersion));
  }

  private void registerCheckConnection(final WorkerFactory factory) {
    final Worker checkConnectionWorker =
        factory.newWorker(TemporalJobType.CHECK_CONNECTION.name(), getWorkerOptions(maxWorkers.getMaxCheckWorkers()));
    checkConnectionWorker.registerWorkflowImplementationTypes(CheckConnectionWorkflowImpl.class);
    checkConnectionWorker
        .registerActivitiesImplementations(
            new CheckConnectionActivityImpl(checkWorkerConfigs, checkProcessFactory, secretsHydrator, workspaceRoot, workerEnvironment, logConfigs,
                jobPersistence, airbyteVersion));
  }

  private void registerGetSpec(final WorkerFactory factory) {
    final Worker specWorker = factory.newWorker(TemporalJobType.GET_SPEC.name(), getWorkerOptions(maxWorkers.getMaxSpecWorkers()));
    specWorker.registerWorkflowImplementationTypes(SpecWorkflowImpl.class);
    specWorker.registerActivitiesImplementations(
        new SpecActivityImpl(specWorkerConfigs, specProcessFactory, workspaceRoot, workerEnvironment, logConfigs, jobPersistence,
            airbyteVersion));
  }

  private ReplicationActivityImpl getReplicationActivityImpl(final WorkerConfigs workerConfigs,
                                                             final ProcessFactory jobProcessFactory) {

    return new ReplicationActivityImpl(
        containerOrchestratorConfig,
        workerConfigs,
        jobProcessFactory,
        secretsHydrator,
        workspaceRoot,
        workerEnvironment,
        logConfigs,
        jobPersistence,
        airbyteVersion,
        featureFlags.useStreamCapableState());
  }

  private NormalizationActivityImpl getNormalizationActivityImpl(final WorkerConfigs workerConfigs,
                                                                 final ProcessFactory jobProcessFactory) {

    return new NormalizationActivityImpl(
        containerOrchestratorConfig,
        workerConfigs,
        jobProcessFactory,
        secretsHydrator,
        workspaceRoot,
        workerEnvironment,
        logConfigs,
        jobPersistence,
        airbyteVersion);
  }

  private DbtTransformationActivityImpl getDbtActivityImpl(final WorkerConfigs workerConfigs,
                                                           final ProcessFactory jobProcessFactory) {

    return new DbtTransformationActivityImpl(
        containerOrchestratorConfig,
        workerConfigs,
        jobProcessFactory,
        secretsHydrator,
        workspaceRoot,
        workerEnvironment,
        logConfigs,
        jobPersistence,
        airbyteVersion);
  }

  /**
   * Return either a docker or kubernetes process factory depending on the environment in
   * {@link WorkerConfigs}
   *
   * @param configs used to determine which process factory to create.
   * @param workerConfigs used to create the process factory.
   * @return either a {@link DockerProcessFactory} or a {@link KubeProcessFactory}.
   * @throws IOException
   */
  private static ProcessFactory getJobProcessFactory(final Configs configs, final WorkerConfigs workerConfigs) throws IOException {
    if (configs.getWorkerEnvironment() == Configs.WorkerEnvironment.KUBERNETES) {
      final KubernetesClient fabricClient = new DefaultKubernetesClient();
      final String localIp = InetAddress.getLocalHost().getHostAddress();
      final String kubeHeartbeatUrl = localIp + ":" + KUBE_HEARTBEAT_PORT;
      LOGGER.info("Using Kubernetes namespace: {}", configs.getJobKubeNamespace());
      return new KubeProcessFactory(workerConfigs,
          configs.getJobKubeNamespace(),
          fabricClient,
          kubeHeartbeatUrl,
          false);
    } else {
      return new DockerProcessFactory(
          workerConfigs,
          configs.getWorkspaceRoot(),
          configs.getWorkspaceDockerMount(),
          configs.getLocalDockerMount(),
          configs.getDockerNetwork());
    }
  }

  private static WorkerOptions getWorkerOptions(final int max) {
    return WorkerOptions.newBuilder()
        .setMaxConcurrentActivityExecutionSize(max)
        .build();
  }

  public record ContainerOrchestratorConfig(
                                            String namespace,
                                            DocumentStoreClient documentStoreClient,
                                            KubernetesClient kubernetesClient,
                                            String secretName,
                                            String secretMountPath,
                                            String containerOrchestratorImage,
                                            String googleApplicationCredentials) {}

  static Optional<ContainerOrchestratorConfig> getContainerOrchestratorConfig(final Configs configs) {
    if (configs.getContainerOrchestratorEnabled()) {
      final var kubernetesClient = new DefaultKubernetesClient();

      final DocumentStoreClient documentStoreClient = StateClients.create(
          configs.getStateStorageCloudConfigs(),
          STATE_STORAGE_PREFIX);

      return Optional.of(new ContainerOrchestratorConfig(
          configs.getJobKubeNamespace(),
          documentStoreClient,
          kubernetesClient,
          configs.getContainerOrchestratorSecretName(),
          configs.getContainerOrchestratorSecretMountPath(),
          configs.getContainerOrchestratorImage(),
          configs.getGoogleApplicationCredentials()));
    } else {
      return Optional.empty();
    }
  }

  private static void launchWorkerApp(final Configs configs, final DSLContext configsDslContext, final DSLContext jobsDslContext) throws IOException {
    MetricClientFactory.initialize(MetricEmittingApps.WORKER);

    final WorkerConfigs defaultWorkerConfigs = new WorkerConfigs(configs);
    final WorkerConfigs specWorkerConfigs = WorkerConfigs.buildSpecWorkerConfigs(configs);
    final WorkerConfigs checkWorkerConfigs = WorkerConfigs.buildCheckWorkerConfigs(configs);
    final WorkerConfigs discoverWorkerConfigs = WorkerConfigs.buildDiscoverWorkerConfigs(configs);
    final WorkerConfigs replicationWorkerConfigs = WorkerConfigs.buildReplicationWorkerConfigs(configs);

    final ProcessFactory defaultProcessFactory = getJobProcessFactory(configs, defaultWorkerConfigs);
    final ProcessFactory specProcessFactory = getJobProcessFactory(configs, specWorkerConfigs);
    final ProcessFactory checkProcessFactory = getJobProcessFactory(configs, checkWorkerConfigs);
    final ProcessFactory discoverProcessFactory = getJobProcessFactory(configs, discoverWorkerConfigs);
    final ProcessFactory replicationProcessFactory = getJobProcessFactory(configs, replicationWorkerConfigs);

    LogClientSingleton.getInstance().setWorkspaceMdc(configs.getWorkerEnvironment(), configs.getLogConfigs(),
        LogClientSingleton.getInstance().getSchedulerLogsRoot(configs.getWorkspaceRoot()));

    final Path workspaceRoot = configs.getWorkspaceRoot();
    LOGGER.info("workspaceRoot = " + workspaceRoot);

    final SecretsHydrator secretsHydrator = SecretPersistence.getSecretsHydrator(configsDslContext, configs);

    if (configs.getWorkerEnvironment().equals(WorkerEnvironment.KUBERNETES)) {
      KubePortManagerSingleton.init(configs.getTemporalWorkerPorts());
    }

    final Database configDatabase = new Database(configsDslContext);
    final FeatureFlags featureFlags = new EnvVariableFeatureFlags();
    final JsonSecretsProcessor jsonSecretsProcessor = JsonSecretsProcessor.builder()
        .maskSecrets(!featureFlags.exposeSecretsInExport())
        .copySecrets(false)
        .build();
    final ConfigPersistence configPersistence = DatabaseConfigPersistence.createWithValidation(configDatabase, jsonSecretsProcessor);
    final ConfigRepository configRepository = new ConfigRepository(configPersistence, configDatabase);

    final Database jobDatabase = new Database(jobsDslContext);

    final JobPersistence jobPersistence = new DefaultJobPersistence(jobDatabase);
    final StatePersistence statePersistence = new StatePersistence(configDatabase);
    final DefaultJobCreator jobCreator = new DefaultJobCreator(
        jobPersistence,
        defaultWorkerConfigs.getResourceRequirements(),
        statePersistence);

    TrackingClientSingleton.initialize(
        configs.getTrackingStrategy(),
        new Deployment(configs.getDeploymentMode(), jobPersistence.getDeployment().orElseThrow(), configs.getWorkerEnvironment()),
        configs.getAirbyteRole(),
        configs.getAirbyteVersion(),
        configRepository);
    final TrackingClient trackingClient = TrackingClientSingleton.get();
    final SyncJobFactory jobFactory = new DefaultSyncJobFactory(
        configs.connectorSpecificResourceDefaultsEnabled(),
        jobCreator,
        configRepository,
        new OAuthConfigSupplier(configRepository, trackingClient));

    final WorkflowServiceStubs temporalService = TemporalUtils.createTemporalService();

    final WorkflowClient workflowClient = TemporalUtils.createWorkflowClient(temporalService, TemporalUtils.getNamespace());
    final StreamResetPersistence streamResetPersistence = new StreamResetPersistence(configDatabase);

    final TemporalClient temporalClient = new TemporalClient(workflowClient, configs.getWorkspaceRoot(), temporalService, streamResetPersistence);
    TemporalUtils.configureTemporalNamespace(temporalService);

    final TemporalWorkerRunFactory temporalWorkerRunFactory = new TemporalWorkerRunFactory(
        temporalClient,
        workspaceRoot,
        configs.getAirbyteVersionOrWarning(),
        featureFlags);

    final WorkspaceHelper workspaceHelper = new WorkspaceHelper(
        configRepository,
        jobPersistence);

    final ConnectionHelper connectionHelper = new ConnectionHelper(configRepository, workspaceHelper);

    final Optional<ContainerOrchestratorConfig> containerOrchestratorConfig = getContainerOrchestratorConfig(configs);

    final WebUrlHelper webUrlHelper = new WebUrlHelper(configs.getWebappUrl());

    final JobNotifier jobNotifier = new JobNotifier(
        webUrlHelper,
        configRepository,
        workspaceHelper,
        TrackingClientSingleton.get());

    final JobTracker jobTracker = new JobTracker(configRepository, jobPersistence, trackingClient);

    final JobErrorReportingClient jobErrorReportingClient = JobErrorReportingClientFactory.getClient(configs.getJobErrorReportingStrategy(), configs);
    final JobErrorReporter jobErrorReporter =
        new JobErrorReporter(
            configRepository,
            configs.getDeploymentMode(),
            configs.getAirbyteVersionOrWarning(),
            webUrlHelper,
            jobErrorReportingClient);

    new WorkerApp(
        workspaceRoot,
        defaultProcessFactory,
        specProcessFactory,
        checkProcessFactory,
        discoverProcessFactory,
        replicationProcessFactory,
        secretsHydrator,
        workflowClient,
        configRepository,
        configs.getMaxWorkers(),
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        defaultWorkerConfigs,
        specWorkerConfigs,
        checkWorkerConfigs,
        discoverWorkerConfigs,
        replicationWorkerConfigs,
        configs.getAirbyteVersionOrWarning(),
        jobFactory,
        jobPersistence,
        temporalWorkerRunFactory,
        configs,
        connectionHelper,
        containerOrchestratorConfig,
        jobNotifier,
        jobTracker,
        jobErrorReporter,
        streamResetPersistence,
        featureFlags,
        jobCreator,
        statePersistence).start();
  }

  public static void main(final String[] args) {
    try {
      final Configs configs = new EnvConfigs();

      final DataSource configsDataSource = DataSourceFactory.create(configs.getConfigDatabaseUser(), configs.getConfigDatabasePassword(),
          DRIVER_CLASS_NAME, configs.getConfigDatabaseUrl());
      final DataSource jobsDataSource = DataSourceFactory.create(configs.getDatabaseUser(), configs.getDatabasePassword(),
          DRIVER_CLASS_NAME, configs.getDatabaseUrl());

      // Manual configuration that will be replaced by Dependency Injection in the future
      try (final DSLContext configsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES);
          final DSLContext jobsDslContext = DSLContextFactory.create(jobsDataSource, SQLDialect.POSTGRES)) {

        // Ensure that the database resources are closed on application shutdown
        CloseableShutdownHook.registerRuntimeShutdownHook(configsDataSource, jobsDataSource, configsDslContext, jobsDslContext);

        final Flyway configsFlyway = FlywayFactory.create(configsDataSource, WorkerApp.class.getSimpleName(),
            ConfigsDatabaseMigrator.DB_IDENTIFIER, ConfigsDatabaseMigrator.MIGRATION_FILE_LOCATION);
        final Flyway jobsFlyway = FlywayFactory.create(jobsDataSource, WorkerApp.class.getSimpleName(), JobsDatabaseMigrator.DB_IDENTIFIER,
            JobsDatabaseMigrator.MIGRATION_FILE_LOCATION);

        // Ensure that the Configuration database is available
        DatabaseCheckFactory
            .createConfigsDatabaseMigrationCheck(configsDslContext, configsFlyway, configs.getConfigsDatabaseMinimumFlywayMigrationVersion(),
                configs.getConfigsDatabaseInitializationTimeoutMs())
            .check();

        LOGGER.info("Checking jobs database flyway migration version..");
        DatabaseCheckFactory.createJobsDatabaseMigrationCheck(jobsDslContext, jobsFlyway, configs.getJobsDatabaseMinimumFlywayMigrationVersion(),
            configs.getJobsDatabaseInitializationTimeoutMs()).check();

        // Ensure that the Jobs database is available
        new JobsDatabaseAvailabilityCheck(jobsDslContext, DatabaseConstants.DEFAULT_ASSERT_DATABASE_TIMEOUT_MS).check();

        launchWorkerApp(configs, configsDslContext, jobsDslContext);
      }
    } catch (final Throwable t) {
      LOGGER.error("Worker app failed", t);
      System.exit(1);
    }
  }

}
