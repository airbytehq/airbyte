/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

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
import io.airbyte.config.persistence.split_secrets.SecretPersistence;
import io.airbyte.config.persistence.split_secrets.SecretsHydrator;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.scheduler.persistence.DefaultJobCreator;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.scheduler.persistence.job_factory.DefaultSyncJobFactory;
import io.airbyte.scheduler.persistence.job_factory.OAuthConfigSupplier;
import io.airbyte.scheduler.persistence.job_factory.SyncJobFactory;
import io.airbyte.workers.helper.ConnectionHelper;
import io.airbyte.workers.process.DockerProcessFactory;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.process.WorkerHeartbeatServer;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.temporal.TemporalJobType;
import io.airbyte.workers.temporal.TemporalUtils;
import io.airbyte.workers.temporal.check.connection.CheckConnectionActivityImpl;
import io.airbyte.workers.temporal.check.connection.CheckConnectionWorkflowImpl;
import io.airbyte.workers.temporal.discover.catalog.DiscoverCatalogActivityImpl;
import io.airbyte.workers.temporal.discover.catalog.DiscoverCatalogWorkflowImpl;
import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflowImpl;
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

  private final Path workspaceRoot;
  private final ProcessFactory jobProcessFactory;
  private final ProcessFactory orchestratorProcessFactory;
  private final SecretsHydrator secretsHydrator;
  private final WorkflowServiceStubs temporalService;
  private final ConfigRepository configRepository;
  private final MaxWorkersConfig maxWorkers;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;
  private final WorkerConfigs workerConfigs;
  private final String databaseUser;
  private final String databasePassword;
  private final String databaseUrl;
  private final String airbyteVersion;
  private final SyncJobFactory jobFactory;
  private final JobPersistence jobPersistence;
  private final TemporalWorkerRunFactory temporalWorkerRunFactory;
  private final Configs configs;
  private final ConnectionHelper connectionHelper;
  private final boolean containerOrchestratorEnabled;

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

    final Worker specWorker = factory.newWorker(TemporalJobType.GET_SPEC.name(), getWorkerOptions(maxWorkers.getMaxSpecWorkers()));
    specWorker.registerWorkflowImplementationTypes(SpecWorkflowImpl.class);
    specWorker.registerActivitiesImplementations(
        new SpecActivityImpl(workerConfigs, jobProcessFactory, workspaceRoot, workerEnvironment, logConfigs, databaseUser, databasePassword,
            databaseUrl,
            airbyteVersion));

    final Worker checkConnectionWorker =
        factory.newWorker(TemporalJobType.CHECK_CONNECTION.name(), getWorkerOptions(maxWorkers.getMaxCheckWorkers()));
    checkConnectionWorker.registerWorkflowImplementationTypes(CheckConnectionWorkflowImpl.class);
    checkConnectionWorker
        .registerActivitiesImplementations(
            new CheckConnectionActivityImpl(workerConfigs, jobProcessFactory, secretsHydrator, workspaceRoot, workerEnvironment, logConfigs,
                databaseUser,
                databasePassword, databaseUrl, airbyteVersion));

    final Worker discoverWorker = factory.newWorker(TemporalJobType.DISCOVER_SCHEMA.name(), getWorkerOptions(maxWorkers.getMaxDiscoverWorkers()));
    discoverWorker.registerWorkflowImplementationTypes(DiscoverCatalogWorkflowImpl.class);
    discoverWorker
        .registerActivitiesImplementations(
            new DiscoverCatalogActivityImpl(workerConfigs, jobProcessFactory, secretsHydrator, workspaceRoot, workerEnvironment, logConfigs,
                databaseUser,
                databasePassword, databaseUrl, airbyteVersion));

    final NormalizationActivityImpl normalizationActivity =
        new NormalizationActivityImpl(
            containerOrchestratorEnabled,
            workerConfigs,
            jobProcessFactory,
            orchestratorProcessFactory,
            secretsHydrator,
            workspaceRoot,
            workerEnvironment,
            logConfigs,
            databaseUser,
            databasePassword,
            databaseUrl,
            airbyteVersion);
    final DbtTransformationActivityImpl dbtTransformationActivity =
        new DbtTransformationActivityImpl(
            containerOrchestratorEnabled,
            workerConfigs,
            jobProcessFactory,
            orchestratorProcessFactory,
            secretsHydrator,
            workspaceRoot,
            workerEnvironment,
            logConfigs,
            databaseUser,
            databasePassword,
            databaseUrl,
            airbyteVersion);
    new PersistStateActivityImpl(workspaceRoot, configRepository);
    final PersistStateActivityImpl persistStateActivity = new PersistStateActivityImpl(workspaceRoot, configRepository);
    final Worker syncWorker = factory.newWorker(TemporalJobType.SYNC.name(), getWorkerOptions(maxWorkers.getMaxSyncWorkers()));
    final ReplicationActivityImpl replicationActivity = getReplicationActivityImpl(
        containerOrchestratorEnabled,
        workerConfigs,
        jobProcessFactory,
        orchestratorProcessFactory,
        secretsHydrator,
        workspaceRoot,
        workerEnvironment,
        logConfigs,
        databaseUser,
        databasePassword,
        databaseUrl,
        airbyteVersion);
    syncWorker.registerWorkflowImplementationTypes(SyncWorkflowImpl.class);

    syncWorker.registerActivitiesImplementations(replicationActivity, normalizationActivity, dbtTransformationActivity, persistStateActivity);

    final Worker connectionUpdaterWorker =
        factory.newWorker(TemporalJobType.CONNECTION_UPDATER.toString(), getWorkerOptions(maxWorkers.getMaxSyncWorkers()));
    connectionUpdaterWorker.registerWorkflowImplementationTypes(ConnectionManagerWorkflowImpl.class, SyncWorkflowImpl.class);
    connectionUpdaterWorker.registerActivitiesImplementations(
        new GenerateInputActivityImpl(
            jobPersistence),
        new JobCreationAndStatusUpdateActivityImpl(
            jobFactory,
            jobPersistence,
            temporalWorkerRunFactory,
            workerEnvironment,
            logConfigs),
        new ConfigFetchActivityImpl(configRepository, jobPersistence, configs, () -> Instant.now().getEpochSecond()),
        new ConnectionDeletionActivityImpl(connectionHelper),
        replicationActivity,
        normalizationActivity,
        dbtTransformationActivity,
        persistStateActivity);

    factory.start();
  }

  /**
   * Switches behavior based on containerOrchestratorEnabled to decide whether to use new container
   * launching or not.
   */
  private ReplicationActivityImpl getReplicationActivityImpl(
                                                             final boolean containerOrchestratorEnabled,
                                                             final WorkerConfigs workerConfigs,
                                                             final ProcessFactory jobProcessFactory,
                                                             final ProcessFactory orchestratorProcessFactory,
                                                             final SecretsHydrator secretsHydrator,
                                                             final Path workspaceRoot,
                                                             final WorkerEnvironment workerEnvironment,
                                                             final LogConfigs logConfigs,
                                                             final String databaseUser,
                                                             final String databasePassword,
                                                             final String databaseUrl,
                                                             final String airbyteVersion) {
    if (containerOrchestratorEnabled) {
      return new ReplicationActivityImpl(
          containerOrchestratorEnabled,
          workerConfigs,
          orchestratorProcessFactory,
          secretsHydrator,
          workspaceRoot,
          workerEnvironment,
          logConfigs,
          databaseUser,
          databasePassword,
          databaseUrl,
          airbyteVersion);
    } else {
      return new ReplicationActivityImpl(
          containerOrchestratorEnabled,
          workerConfigs,
          jobProcessFactory,
          secretsHydrator,
          workspaceRoot,
          workerEnvironment,
          logConfigs,
          databaseUser,
          databasePassword,
          databaseUrl,
          airbyteVersion);
    }
  }

  private static ProcessFactory getJobProcessFactory(final Configs configs) throws IOException {
    final WorkerConfigs workerConfigs = new WorkerConfigs(configs);

    if (configs.getWorkerEnvironment() == Configs.WorkerEnvironment.KUBERNETES) {
      final KubernetesClient fabricClient = new DefaultKubernetesClient();
      final String localIp = InetAddress.getLocalHost().getHostAddress();
      final String kubeHeartbeatUrl = localIp + ":" + KUBE_HEARTBEAT_PORT;
      LOGGER.info("Using Kubernetes namespace: {}", configs.getJobKubeNamespace());
      return new KubeProcessFactory(workerConfigs, configs.getJobKubeNamespace(), fabricClient, kubeHeartbeatUrl, false);
    } else {
      return new DockerProcessFactory(
          workerConfigs,
          configs.getWorkspaceRoot(),
          configs.getWorkspaceDockerMount(),
          configs.getLocalDockerMount(),
          configs.getDockerNetwork(),
          false);
    }
  }

  private static ProcessFactory getOrchestratorProcessFactory(final Configs configs) throws IOException {
    final WorkerConfigs workerConfigs = new WorkerConfigs(configs);

    if (configs.getWorkerEnvironment() == Configs.WorkerEnvironment.KUBERNETES) {
      final KubernetesClient fabricClient = new DefaultKubernetesClient();
      final String localIp = InetAddress.getLocalHost().getHostAddress();
      final String kubeHeartbeatUrl = localIp + ":" + KUBE_HEARTBEAT_PORT;
      LOGGER.info("Using Kubernetes namespace: {}", configs.getJobKubeNamespace());
      return new KubeProcessFactory(workerConfigs, configs.getJobKubeNamespace(), fabricClient, kubeHeartbeatUrl, true);
    } else {
      return new DockerProcessFactory(
          workerConfigs,
          configs.getWorkspaceRoot(),
          configs.getWorkspaceDockerMount(),
          configs.getLocalDockerMount(),

          // this needs to point at the Docker network Airbyte is running on, not the host network or job
          // runner network, otherwise it can't talk with the db/minio
          "airbyte_default",

          true);
    }
  }

  private static WorkerOptions getWorkerOptions(final int max) {
    return WorkerOptions.newBuilder()
        .setMaxConcurrentActivityExecutionSize(max)
        .build();
  }

  public static void main(final String[] args) throws IOException, InterruptedException {
    final Configs configs = new EnvConfigs();

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

    final ProcessFactory jobProcessFactory = getJobProcessFactory(configs);
    final ProcessFactory orchestratorProcessFactory = getOrchestratorProcessFactory(configs);

    final WorkflowServiceStubs temporalService = TemporalUtils.createTemporalService(temporalHost);

    final Database configDatabase = new ConfigsDatabaseInstance(
        configs.getConfigDatabaseUser(),
        configs.getConfigDatabasePassword(),
        configs.getConfigDatabaseUrl())
            .getInitialized();
    final ConfigPersistence configPersistence = new DatabaseConfigPersistence(configDatabase).withValidation();
    final Optional<SecretPersistence> secretPersistence = SecretPersistence.getLongLived(configs);
    final Optional<SecretPersistence> ephemeralSecretPersistence = SecretPersistence.getEphemeral(configs);
    final ConfigRepository configRepository = new ConfigRepository(configPersistence, secretsHydrator, secretPersistence, ephemeralSecretPersistence);

    final Database jobDatabase = new JobsDatabaseInstance(
        configs.getDatabaseUser(),
        configs.getDatabasePassword(),
        configs.getDatabaseUrl())
            .getInitialized();

    final JobPersistence jobPersistence = new DefaultJobPersistence(jobDatabase);
    final TrackingClient trackingClient = TrackingClientSingleton.get();
    final SyncJobFactory jobFactory = new DefaultSyncJobFactory(
        new DefaultJobCreator(jobPersistence, configRepository),
        configRepository,
        new OAuthConfigSupplier(configRepository, trackingClient));

    final TemporalClient temporalClient = TemporalClient.production(temporalHost, workspaceRoot, configs);

    final FeatureFlags featureFlags = new EnvVariableFeatureFlags();

    final TemporalWorkerRunFactory temporalWorkerRunFactory = new TemporalWorkerRunFactory(
        temporalClient,
        workspaceRoot,
        configs.getAirbyteVersionOrWarning(),
        featureFlags);

    final WorkspaceHelper workspaceHelper = new WorkspaceHelper(
        configRepository,
        jobPersistence);

    final WorkerConfigs workerConfigs = new WorkerConfigs(configs);

    final ConnectionHelper connectionHelper = new ConnectionHelper(
        configRepository,
        workspaceHelper,
        workerConfigs);

    new WorkerApp(
        workspaceRoot,
        jobProcessFactory,
        orchestratorProcessFactory,
        secretsHydrator,
        temporalService,
        configRepository,
        configs.getMaxWorkers(),
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        workerConfigs,
        configs.getDatabaseUser(),
        configs.getDatabasePassword(),
        configs.getDatabaseUrl(),
        configs.getAirbyteVersionOrWarning(),
        jobFactory,
        jobPersistence,
        temporalWorkerRunFactory,
        configs,
        connectionHelper,
        configs.getContainerOrchestratorEnabled()).start();
  }

}
