/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.analytics.Deployment;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.MaxWorkersConfig;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.metrics.lib.DatadogClientConfiguration;
import io.airbyte.metrics.lib.DogStatsDMetricSingleton;
import io.airbyte.metrics.lib.MetricEmittingApps;
import io.airbyte.scheduler.persistence.DefaultJobCreator;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobCreator;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.scheduler.persistence.job_factory.DefaultSyncJobFactory;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.workers.helper.ConnectionHelper;
import io.airbyte.workers.process.DockerProcessFactory;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.process.WorkerHeartbeatServer;
import io.airbyte.workers.storage.DocumentStoreClient;
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
import io.airbyte.workers.temporal.spec.SpecActivityImpl;
import io.airbyte.workers.temporal.spec.SpecWorkflowImpl;
import io.airbyte.workers.temporal.sync.DbtTransformationActivityImpl;
import io.airbyte.workers.temporal.sync.NormalizationActivityImpl;
import io.airbyte.workers.temporal.sync.PersistStateActivityImpl;
import io.airbyte.workers.temporal.sync.ReplicationActivityImpl;
import io.airbyte.workers.temporal.sync.SyncWorkflowImpl;
import io.airbyte.workers.worker_run.TemporalWorkerRunFactory;
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
import lombok.AllArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

@AllArgsConstructor
public class WorkerApp {

  private static final Logger LOGGER = LoggerFactory.getLogger(WorkerApp.class);
  public static final int KUBE_HEARTBEAT_PORT = 9000;

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
  private final WorkflowServiceStubs temporalService;
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

    final WorkerFactory factory = WorkerFactory.newInstance(WorkflowClient.newInstance(temporalService));

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
    final JobCreator jobCreator = new DefaultJobCreator(jobPersistence, configRepository, defaultWorkerConfigs.getResourceRequirements());
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
            jobCreator),
        new ConfigFetchActivityImpl(configRepository, jobPersistence, configs, () -> Instant.now().getEpochSecond()),
        new ConnectionDeletionActivityImpl(connectionHelper),
        new AutoDisableConnectionActivityImpl(configRepository, jobPersistence, featureFlags, configs, jobNotifier));
  }

  private void registerSync(final WorkerFactory factory) {
    final ReplicationActivityImpl replicationActivity = getReplicationActivityImpl(replicationWorkerConfigs, replicationProcessFactory);

    final NormalizationActivityImpl normalizationActivity = getNormalizationActivityImpl(
        defaultWorkerConfigs,
        defaultProcessFactory);

    final DbtTransformationActivityImpl dbtTransformationActivity = getDbtActivityImpl(
        defaultWorkerConfigs,
        defaultProcessFactory);

    final CheckConnectionActivityImpl checkConnectionActivity =
        new CheckConnectionActivityImpl(checkWorkerConfigs, checkProcessFactory, secretsHydrator, workspaceRoot, workerEnvironment, logConfigs,
            jobPersistence, airbyteVersion);

    final PersistStateActivityImpl persistStateActivity = new PersistStateActivityImpl(workspaceRoot, configRepository);

    final Worker syncWorker = factory.newWorker(TemporalJobType.SYNC.name(), getWorkerOptions(maxWorkers.getMaxSyncWorkers()));
    syncWorker.registerWorkflowImplementationTypes(SyncWorkflowImpl.class);
    syncWorker.registerActivitiesImplementations(checkConnectionActivity, replicationActivity, normalizationActivity, dbtTransformationActivity, persistStateActivity);
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
        airbyteVersion);
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

  public static record ContainerOrchestratorConfig(
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

  private static void launchWorkerApp() throws IOException {
    final Configs configs = new EnvConfigs();

    DogStatsDMetricSingleton.initialize(MetricEmittingApps.WORKER, new DatadogClientConfiguration(configs));

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

    final String temporalHost = configs.getTemporalHost();
    LOGGER.info("temporalHost = " + temporalHost);

    final SecretsHydrator secretsHydrator = SecretPersistence.getSecretsHydrator(configs);

    if (configs.getWorkerEnvironment().equals(WorkerEnvironment.KUBERNETES)) {
      KubePortManagerSingleton.init(configs.getTemporalWorkerPorts());
    }

    final WorkflowServiceStubs temporalService = TemporalUtils.createTemporalService(temporalHost);

    TemporalUtils.configureTemporalNamespace(temporalService);

    final Database configDatabase = new ConfigsDatabaseInstance(
        configs.getConfigDatabaseUser(),
        configs.getConfigDatabasePassword(),
        configs.getConfigDatabaseUrl())
            .getInitialized();
    final FeatureFlags featureFlags = new EnvVariableFeatureFlags();
    final JsonSecretsProcessor jsonSecretsProcessor = JsonSecretsProcessor.builder()
        .maskSecrets(!featureFlags.exposeSecretsInExport())
        .copySecrets(false)
        .build();
    final ConfigPersistence configPersistence = DatabaseConfigPersistence.createWithValidation(configDatabase, jsonSecretsProcessor);
    final ConfigRepository configRepository = new ConfigRepository(configPersistence, configDatabase);

    final Database jobDatabase = new JobsDatabaseInstance(
        configs.getDatabaseUser(),
        configs.getDatabasePassword(),
        configs.getDatabaseUrl())
            .getInitialized();

    final JobPersistence jobPersistence = new DefaultJobPersistence(jobDatabase);
    TrackingClientSingleton.initialize(
        configs.getTrackingStrategy(),
        new Deployment(configs.getDeploymentMode(), jobPersistence.getDeployment().orElseThrow(), configs.getWorkerEnvironment()),
        configs.getAirbyteRole(),
        configs.getAirbyteVersion(),
        configRepository);
    final TrackingClient trackingClient = TrackingClientSingleton.get();
    final SyncJobFactory jobFactory = new DefaultSyncJobFactory(
        configs.connectorSpecificResourceDefaultsEnabled(),
        new DefaultJobCreator(jobPersistence, configRepository, defaultWorkerConfigs.getResourceRequirements()),
        configRepository,
        new OAuthConfigSupplier(configRepository, trackingClient));

    final TemporalClient temporalClient = TemporalClient.production(temporalHost, workspaceRoot, configs);

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

    final JobNotifier jobNotifier = new JobNotifier(
        configs.getWebappUrl(),
        configRepository,
        workspaceHelper,
        TrackingClientSingleton.get());

    final JobTracker jobTracker = new JobTracker(configRepository, jobPersistence, trackingClient);

    new WorkerApp(
        workspaceRoot,
        defaultProcessFactory,
        specProcessFactory,
        checkProcessFactory,
        discoverProcessFactory,
        replicationProcessFactory,
        secretsHydrator,
        temporalService,
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
        jobTracker).start();
  }

  public static void main(final String[] args) {
    try {
      launchWorkerApp();
    } catch (final Throwable t) {
      LOGGER.error("Worker app failed", t);
      System.exit(1);
    }
  }

}
