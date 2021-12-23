/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

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
import io.airbyte.workers.process.DockerProcessFactory;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.process.KubeProcessFactory;
import io.airbyte.workers.process.ProcessFactory;
import io.airbyte.workers.process.WorkerHeartbeatServer;
import io.airbyte.workers.temporal.TemporalJobType;
import io.airbyte.workers.temporal.TemporalUtils;
import io.airbyte.workers.temporal.check.connection.CheckConnectionActivityImpl;
import io.airbyte.workers.temporal.check.connection.CheckConnectionWorkflowImpl;
import io.airbyte.workers.temporal.discover.catalog.DiscoverCatalogActivityImpl;
import io.airbyte.workers.temporal.discover.catalog.DiscoverCatalogWorkflowImpl;
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
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.Executors;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

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
  private final boolean containerOrchestratorEnabled;

  public WorkerApp(final Path workspaceRoot,
                   final ProcessFactory jobProcessFactory,
                   final ProcessFactory orchestratorProcessFactory,
                   final SecretsHydrator secretsHydrator,
                   final WorkflowServiceStubs temporalService,
                   final MaxWorkersConfig maxWorkers,
                   final ConfigRepository configRepository,
                   final WorkerEnvironment workerEnvironment,
                   final LogConfigs logConfigs,
                   final WorkerConfigs workerConfigs,
                   final String databaseUser,
                   final String databasePassword,
                   final String databaseUrl,
                   final String airbyteVersion,
                   final boolean containerOrchestratorEnabled) {

    this.workspaceRoot = workspaceRoot;
    this.jobProcessFactory = jobProcessFactory;
    this.orchestratorProcessFactory = orchestratorProcessFactory;
    this.secretsHydrator = secretsHydrator;
    this.temporalService = temporalService;
    this.maxWorkers = maxWorkers;
    this.configRepository = configRepository;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
    this.workerConfigs = workerConfigs;
    this.databaseUser = databaseUser;
    this.databasePassword = databasePassword;
    this.databaseUrl = databaseUrl;
    this.airbyteVersion = airbyteVersion;
    this.containerOrchestratorEnabled = containerOrchestratorEnabled;
  }

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

    final Worker syncWorker = factory.newWorker(TemporalJobType.SYNC.name(), getWorkerOptions(maxWorkers.getMaxSyncWorkers()));
    final ReplicationActivityImpl replicationActivityImpl = getReplicationActivityImpl(
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
    syncWorker.registerActivitiesImplementations(
        replicationActivityImpl,
        new NormalizationActivityImpl(workerConfigs, jobProcessFactory, secretsHydrator, workspaceRoot, workerEnvironment, logConfigs, databaseUser,
            databasePassword, databaseUrl, airbyteVersion),
        new DbtTransformationActivityImpl(workerConfigs, jobProcessFactory, secretsHydrator, workspaceRoot, workerEnvironment, logConfigs,
            databaseUser,
            databasePassword, databaseUrl, airbyteVersion),
        new PersistStateActivityImpl(workspaceRoot, configRepository));

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

    new WorkerApp(
        workspaceRoot,
        jobProcessFactory,
        orchestratorProcessFactory,
        secretsHydrator,
        temporalService,
        configs.getMaxWorkers(),
        configRepository,
        configs.getWorkerEnvironment(),
        configs.getLogConfigs(),
        new WorkerConfigs(configs),
        configs.getDatabaseUser(),
        configs.getDatabasePassword(),
        configs.getDatabaseUrl(),
        configs.getAirbyteVersionOrWarning(),
        configs.getContainerOrchestratorEnabled()).start();
  }

}
