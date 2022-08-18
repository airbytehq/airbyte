/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import com.auth0.jwt.JWT;
import com.auth0.jwt.JWTCreator;
import com.auth0.jwt.algorithms.Algorithm;
import com.google.auth.oauth2.ServiceAccountCredentials;
import io.airbyte.analytics.Deployment;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.lang.CloseableShutdownHook;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.config.persistence.StreamResetPersistence;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.db.Database;
import io.airbyte.db.check.DatabaseCheckException;
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
import io.airbyte.workers.temporal.sync.DecideDataPlaneTaskQueueActivityImpl;
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
import java.io.FileInputStream;
import java.io.IOException;
import java.net.InetAddress;
import java.nio.file.Path;
import java.security.interfaces.RSAPrivateKey;
import java.time.Instant;
import java.util.Date;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import javax.annotation.Nullable;
import javax.sql.DataSource;
import org.flywaydb.core.Flyway;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

@SuppressWarnings("PMD.AvoidCatchingThrowable")
public class WorkerApp {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerApp.class);
  public static final int KUBE_HEARTBEAT_PORT = 9000;
  private static final String DRIVER_CLASS_NAME = DatabaseDriver.POSTGRESQL.getDriverClassName();

  // IMPORTANT: Changing the storage location will orphan already existing kube pods when the new
  // version is deployed!
  public static final Path STATE_STORAGE_PREFIX = Path.of("/state");
  private static final int JWT_TTL_MINUTES = 5;

  private static Configs configs;
  private static ProcessFactory defaultProcessFactory;
  private static ProcessFactory specProcessFactory;
  private static ProcessFactory checkProcessFactory;
  private static ProcessFactory discoverProcessFactory;
  private static ProcessFactory replicationProcessFactory;
  private static SecretsHydrator secretsHydrator;
  private static WorkflowClient workflowClient;
  private static ConfigRepository configRepository;
  private static WorkerConfigs defaultWorkerConfigs;
  private static WorkerConfigs specWorkerConfigs;
  private static WorkerConfigs checkWorkerConfigs;
  private static WorkerConfigs discoverWorkerConfigs;
  private static WorkerConfigs replicationWorkerConfigs;
  private static SyncJobFactory jobFactory;
  private static JobPersistence jobPersistence;
  private static WorkflowServiceStubs temporalService;
  private static TemporalWorkerRunFactory temporalWorkerRunFactory;
  private static ConnectionHelper connectionHelper;
  private static Optional<ContainerOrchestratorConfig> containerOrchestratorConfig;
  private static JobNotifier jobNotifier;
  private static JobTracker jobTracker;
  private static JobErrorReporter jobErrorReporter;
  private static StreamResetPersistence streamResetPersistence;
  private static FeatureFlags featureFlags;
  private static DefaultJobCreator jobCreator;
  private static AirbyteApiClient airbyteApiClient;

  private static void registerConnectionManager(final WorkerFactory factory) {
    final FeatureFlags featureFlags = new EnvVariableFeatureFlags();

    final Worker connectionUpdaterWorker =
        factory.newWorker(TemporalJobType.CONNECTION_UPDATER.toString(), getWorkerOptions(configs.getMaxWorkers().getMaxSyncWorkers()));
    connectionUpdaterWorker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class);
    connectionUpdaterWorker.registerActivitiesImplementations(
        new GenerateInputActivityImpl(
            jobPersistence),
        new JobCreationAndStatusUpdateActivityImpl(
            jobFactory,
            jobPersistence,
            temporalWorkerRunFactory,
            configs.getWorkerEnvironment(),
            configs.getLogConfigs(),
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
            configs.getWorkspaceRoot(),
            configs.getWorkerEnvironment(),
            configs.getLogConfigs(),
            airbyteApiClient,
            configs.getAirbyteVersionOrWarning()),
        new AutoDisableConnectionActivityImpl(configRepository, jobPersistence, featureFlags, configs, jobNotifier),
        new StreamResetActivityImpl(streamResetPersistence, jobPersistence));
  }

  private static void registerSync(final WorkerFactory factory) {
    registerSyncDataPlaneWorkers(factory);
    registerSyncControlPlaneWorkers(factory);
  }

  /**
   * Data Plane workers handle the subset of SyncWorkflow activity tasks that should run within a Data
   * Plane.
   */
  private static void registerSyncDataPlaneWorkers(final WorkerFactory factory) {
    if (configs.isDataPlaneWorker() && !configs.getDataPlaneTaskQueues().isEmpty()) {
      final ReplicationActivityImpl replicationActivity = getReplicationActivityImpl(replicationWorkerConfigs, replicationProcessFactory);
      // Note that the configuration injected here is for the normalization orchestrator, and not the
      // normalization pod itself.
      // Configuration for the normalization pod is injected via the SyncWorkflowImpl.
      final NormalizationActivityImpl normalizationActivity = getNormalizationActivityImpl(defaultWorkerConfigs, defaultProcessFactory);
      final DbtTransformationActivityImpl dbtTransformationActivity = getDbtActivityImpl(
          defaultWorkerConfigs,
          defaultProcessFactory);
      final PersistStateActivityImpl persistStateActivity = new PersistStateActivityImpl(airbyteApiClient, featureFlags);

      for (final String taskQueue : configs.getDataPlaneTaskQueues()) {
        // TODO (parker) consider separating out maxSyncActivityWorkers and maxSyncWorkflowWorkers
        final Worker worker = factory.newWorker(taskQueue, getWorkerOptions(configs.getMaxWorkers().getMaxSyncWorkers()));
        worker.registerActivitiesImplementations(replicationActivity, normalizationActivity, dbtTransformationActivity, persistStateActivity);
      }
    }
  }

  /**
   * Control Plane workers handle all workflow tasks for the SyncWorkflow, as well as the activity
   * task to decide which task queue to use for Data Plane tasks.
   */
  private static void registerSyncControlPlaneWorkers(final WorkerFactory factory) {
    if (configs.isControlPlaneWorker()) {
      // TODO (parker) consider separating out maxSyncActivityWorkers and maxSyncWorkflowWorkers
      final Worker syncWorker = factory.newWorker(TemporalJobType.SYNC.name(), getWorkerOptions(configs.getMaxWorkers().getMaxSyncWorkers()));
      syncWorker.registerWorkflowImplementationTypes(SyncWorkflowImpl.class);

      final DecideDataPlaneTaskQueueActivityImpl decideTaskQueueActivity = getDecideTaskQueueActivityImpl();
      syncWorker.registerActivitiesImplementations(decideTaskQueueActivity);
    }
  }

  private static void registerDiscover(final WorkerFactory factory) {
    final Worker discoverWorker = factory.newWorker(TemporalJobType.DISCOVER_SCHEMA.name(),
        getWorkerOptions(configs.getMaxWorkers().getMaxDiscoverWorkers()));
    discoverWorker.registerWorkflowImplementationTypes(DiscoverCatalogWorkflowImpl.class);
    discoverWorker
        .registerActivitiesImplementations(
            new DiscoverCatalogActivityImpl(discoverWorkerConfigs, discoverProcessFactory, secretsHydrator, configs.getWorkspaceRoot(),
                configs.getWorkerEnvironment(),
                configs.getLogConfigs(),
                airbyteApiClient, configs.getAirbyteVersionOrWarning()));
  }

  private static void registerCheckConnection(final WorkerFactory factory) {
    final Worker checkConnectionWorker =
        factory.newWorker(TemporalJobType.CHECK_CONNECTION.name(), getWorkerOptions(configs.getMaxWorkers().getMaxCheckWorkers()));
    checkConnectionWorker.registerWorkflowImplementationTypes(CheckConnectionWorkflowImpl.class);
    checkConnectionWorker
        .registerActivitiesImplementations(
            new CheckConnectionActivityImpl(checkWorkerConfigs, checkProcessFactory, secretsHydrator, configs.getWorkspaceRoot(),
                configs.getWorkerEnvironment(), configs.getLogConfigs(),
                airbyteApiClient, configs.getAirbyteVersionOrWarning()));
  }

  private static void registerGetSpec(final WorkerFactory factory) {
    final Worker specWorker = factory.newWorker(TemporalJobType.GET_SPEC.name(), getWorkerOptions(configs.getMaxWorkers().getMaxSpecWorkers()));
    specWorker.registerWorkflowImplementationTypes(SpecWorkflowImpl.class);
    specWorker.registerActivitiesImplementations(
        new SpecActivityImpl(specWorkerConfigs, specProcessFactory, configs.getWorkspaceRoot(), configs.getWorkerEnvironment(),
            configs.getLogConfigs(), airbyteApiClient,
            configs.getAirbyteVersionOrWarning()));
  }

  private static ReplicationActivityImpl getReplicationActivityImpl(final WorkerConfigs workerConfigs,
                                                                    final ProcessFactory jobProcessFactory) {

    return new ReplicationActivityImpl(
        containerOrchestratorConfig,
        workerConfigs,
        jobProcessFactory,
        secretsHydrator,
        configs.getWorkspaceRoot(),
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        airbyteApiClient,
        configs.getAirbyteVersionOrWarning(),
        featureFlags.useStreamCapableState());
  }

  private static NormalizationActivityImpl getNormalizationActivityImpl(final WorkerConfigs workerConfigs,
                                                                        final ProcessFactory jobProcessFactory) {

    return new NormalizationActivityImpl(
        containerOrchestratorConfig,
        workerConfigs,
        jobProcessFactory,
        secretsHydrator,
        configs.getWorkspaceRoot(),
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        jobPersistence,
        airbyteApiClient,
        configs.getAirbyteVersionOrWarning());
  }

  private static DbtTransformationActivityImpl getDbtActivityImpl(final WorkerConfigs workerConfigs,
                                                                  final ProcessFactory jobProcessFactory) {

    return new DbtTransformationActivityImpl(
        containerOrchestratorConfig,
        workerConfigs,
        jobProcessFactory,
        secretsHydrator,
        configs.getWorkspaceRoot(),
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        jobPersistence,
        airbyteApiClient,
        configs.getAirbyteVersionOrWarning());
  }

  private static DecideDataPlaneTaskQueueActivityImpl getDecideTaskQueueActivityImpl() {
    return new DecideDataPlaneTaskQueueActivityImpl(configs);
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
    if (configs.getWorkerEnvironment().equals(Configs.WorkerEnvironment.KUBERNETES)) {
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
                                            String googleApplicationCredentials) {

  }

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

  private static AirbyteApiClient getApiClient(final Configs configs) {
    final var authHeader = configs.getAirbyteApiAuthHeaderName();

    // control plane workers communicate with the Airbyte API within their internal network, so https
    // isn't needed
    final var scheme = configs.isControlPlaneWorker() ? "http" : "https";

    LOGGER.debug("Creating Airbyte Config Api Client with Scheme: {}, Host: {}, Port: {}, Auth-Header: {}",
        scheme, configs.getAirbyteApiHost(), configs.getAirbyteApiPort(), authHeader);

    final AirbyteApiClient airbyteApiClient = new AirbyteApiClient(
        new io.airbyte.api.client.invoker.generated.ApiClient()
            .setScheme(scheme)
            .setHost(configs.getAirbyteApiHost())
            .setPort(configs.getAirbyteApiPort())
            .setBasePath("/api")
            .setRequestInterceptor(builder -> {
              builder.setHeader(authHeader, generateAuthToken());
              builder.setHeader("User-Agent", "WorkerApp");
            }));
    return airbyteApiClient;
  }

  /**
   * Generate an auth token based on configs. This is called by the Api Client's requestInterceptor
   * for each request.
   *
   * For Data Plane workers, generate a signed JWT as described here:
   * https://cloud.google.com/endpoints/docs/openapi/service-account-authentication
   *
   * Otherwise, use the AIRBYTE_API_AUTH_HEADER_VALUE from EnvConfigs.
   */
  private static String generateAuthToken() {
    if (configs.isControlPlaneWorker()) {
      // control plane workers communicate with the Airbyte API within their internal network, so a signed
      // JWT isn't needed
      return configs.getAirbyteApiAuthHeaderValue();
    } else if (configs.isDataPlaneWorker()) {
      try {
        final Date now = new Date();
        final Date expTime = new Date(System.currentTimeMillis() + TimeUnit.MINUTES.toMillis(JWT_TTL_MINUTES));
        final String saEmail = configs.getDataPlaneServiceAccountEmail();
        // Build the JWT payload
        final JWTCreator.Builder token = JWT.create()
            .withIssuedAt(now)
            // Expires after 'expiryLength' seconds
            .withExpiresAt(expTime)
            // Must match 'issuer' in the security configuration in your
            // swagger spec (e.g. service account email)
            .withIssuer(saEmail)
            // Must be either your Endpoints service name, or match the value
            // specified as the 'x-google-audience' in the OpenAPI document
            .withAudience(configs.getControlPlaneGoogleEndpoint())
            // Subject and email should match the service account's email
            .withSubject(saEmail)
            .withClaim("email", saEmail);

        // TODO multi-cloud phase 2: check performance of on-demand token generation in load testing. might
        // need
        // to pull some of this outside of this method which is called for every API request
        final FileInputStream stream = new FileInputStream(configs.getDataPlaneServiceAccountCredentialsPath());
        final ServiceAccountCredentials cred = ServiceAccountCredentials.fromStream(stream);
        final RSAPrivateKey key = (RSAPrivateKey) cred.getPrivateKey();
        final Algorithm algorithm = Algorithm.RSA256(null, key);
        return "Bearer " + token.sign(algorithm);
      } catch (final Throwable t) {
        LOGGER.warn("An issue occurred while generating a data plane auth token. Defaulting to empty string.", t);
        return "";
      }
    } else {
      // shouldn't be possible to reach this state since a worker must be at least one of control/data
      // plane
      LOGGER.warn("Worker somehow wasn't a control plane or a data plane worker!");
      return "";
    }
  }

  public static void start() {
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

  private static void initializeCommonDependencies() {
    LOGGER.debug("Initializing common worker dependencies.");
    configs = new EnvConfigs();
    LOGGER.info("workspaceRoot = " + configs.getWorkspaceRoot());

    MetricClientFactory.initialize(MetricEmittingApps.WORKER);

    LogClientSingleton.getInstance().setWorkspaceMdc(
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        LogClientSingleton.getInstance().getSchedulerLogsRoot(configs.getWorkspaceRoot()));

    if (configs.getWorkerEnvironment().equals(WorkerEnvironment.KUBERNETES)) {
      KubePortManagerSingleton.init(configs.getTemporalWorkerPorts());
    }

    featureFlags = new EnvVariableFeatureFlags();
    defaultWorkerConfigs = new WorkerConfigs(configs);
    temporalService = TemporalUtils.createTemporalService();
    workflowClient = TemporalUtils.createWorkflowClient(temporalService, TemporalUtils.getNamespace());
    TemporalUtils.configureTemporalNamespace(temporalService);
    airbyteApiClient = getApiClient(configs);
  }

  private static void initializeControlPlaneDependencies() throws IOException, DatabaseCheckException {
    if (!configs.isControlPlaneWorker()) {
      LOGGER.debug("Skipping Control Plane dependency initialization.");
      return;
    }
    LOGGER.debug("Initializing control plane worker dependencies.");

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

      specWorkerConfigs = WorkerConfigs.buildSpecWorkerConfigs(configs);
      checkWorkerConfigs = WorkerConfigs.buildCheckWorkerConfigs(configs);
      discoverWorkerConfigs = WorkerConfigs.buildDiscoverWorkerConfigs(configs);

      specProcessFactory = getJobProcessFactory(configs, specWorkerConfigs);
      checkProcessFactory = getJobProcessFactory(configs, checkWorkerConfigs);
      discoverProcessFactory = getJobProcessFactory(configs, discoverWorkerConfigs);

      final Database configDatabase = new Database(configsDslContext);
      final JsonSecretsProcessor jsonSecretsProcessor = JsonSecretsProcessor.builder()
          .maskSecrets(!featureFlags.exposeSecretsInExport())
          .copySecrets(false)
          .build();
      final ConfigPersistence configPersistence = DatabaseConfigPersistence.createWithValidation(configDatabase, jsonSecretsProcessor);
      configRepository = new ConfigRepository(configPersistence, configDatabase);

      final Database jobDatabase = new Database(jobsDslContext);

      jobPersistence = new DefaultJobPersistence(jobDatabase);
      final StatePersistence statePersistence = new StatePersistence(configDatabase);
      jobCreator = new DefaultJobCreator(
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
      jobFactory = new DefaultSyncJobFactory(
          configs.connectorSpecificResourceDefaultsEnabled(),
          jobCreator,
          configRepository,
          new OAuthConfigSupplier(configRepository, trackingClient));

      streamResetPersistence = new StreamResetPersistence(configDatabase);

      final TemporalClient temporalClient = new TemporalClient(workflowClient, configs.getWorkspaceRoot(), temporalService, streamResetPersistence);

      temporalWorkerRunFactory = new TemporalWorkerRunFactory(
          temporalClient,
          configs.getWorkspaceRoot(),
          configs.getAirbyteVersionOrWarning(),
          featureFlags);

      final WorkspaceHelper workspaceHelper = new WorkspaceHelper(
          configRepository,
          jobPersistence);

      connectionHelper = new ConnectionHelper(configRepository, workspaceHelper);

      final WebUrlHelper webUrlHelper = new WebUrlHelper(configs.getWebappUrl());

      jobNotifier = new JobNotifier(
          webUrlHelper,
          configRepository,
          workspaceHelper,
          TrackingClientSingleton.get());

      jobTracker = new JobTracker(configRepository, jobPersistence, trackingClient);

      final JobErrorReportingClient jobErrorReportingClient = JobErrorReportingClientFactory.getClient(configs.getJobErrorReportingStrategy(),
          configs);
      jobErrorReporter = new JobErrorReporter(
          configRepository,
          configs.getDeploymentMode(),
          configs.getAirbyteVersionOrWarning(),
          webUrlHelper,
          jobErrorReportingClient);

      initializeSecretsHydrator(configsDslContext);
    }
  }

  private static void initializeDataPlaneDependencies() throws IOException {
    if (!configs.isDataPlaneWorker()) {
      LOGGER.debug("Skipping Data Plane dependency initialization.");
      return;
    }
    LOGGER.debug("Initializing data plane worker dependencies.");

    replicationWorkerConfigs = WorkerConfigs.buildReplicationWorkerConfigs(configs);

    defaultProcessFactory = getJobProcessFactory(configs, defaultWorkerConfigs);
    replicationProcessFactory = getJobProcessFactory(configs, replicationWorkerConfigs);

    containerOrchestratorConfig = getContainerOrchestratorConfig(configs);
    initializeSecretsHydrator(null);
  }

  /**
   * The secretsHydrator is a common dependency for both Control Plane and Data Plane workers. In some
   * cases, it uses a database as its backing persistence, so a configsDslContext is passed in.
   * However, Data Plane workers don't support using a database as a backing store, and the
   * configsDslContext doesn't exist in that case. So, this method can be called multiple times, with
   * or without a configsDslContext, to initialize the secretsHydrator correctly based on the type of
   * worker.
   */
  private static void initializeSecretsHydrator(final @Nullable DSLContext configsDslContext) {
    if (secretsHydrator != null) {
      LOGGER.debug("secretsHydrator was already initialized!");
      return;
    }

    if (configs.isControlPlaneWorker()) {
      secretsHydrator = SecretPersistence.getSecretsHydrator(configsDslContext, configs);
    } else {
      // Data Plane-only workers call a dedicated method to get a secretsHydrator without a
      // configsDslContext
      secretsHydrator = SecretPersistence.getDataPlaneSecretsHydrator(configs);
    }
  }

  public static void main(final String[] args) {
    try {
      initializeCommonDependencies();
      initializeControlPlaneDependencies();
      initializeDataPlaneDependencies();
      start();
    } catch (final Throwable t) {
      LOGGER.error("Worker app failed", t);
      System.exit(1);
    }
  }

}
