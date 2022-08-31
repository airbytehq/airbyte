/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import io.airbyte.analytics.Deployment;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.Configs.TrackingStrategy;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.Configs.WorkerPlane;
import io.airbyte.config.MaxWorkersConfig;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.db.check.DatabaseCheckException;
import io.airbyte.db.check.DatabaseMigrationCheck;
import io.airbyte.db.check.impl.JobsDatabaseAvailabilityCheck;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.metrics.lib.MetricEmittingApps;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.temporal.TemporalJobType;
import io.airbyte.workers.temporal.TemporalProxyHelper;
import io.airbyte.workers.temporal.TemporalUtils;
import io.airbyte.workers.temporal.check.connection.CheckConnectionWorkflowImpl;
import io.airbyte.workers.temporal.discover.catalog.DiscoverCatalogWorkflowImpl;
import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflowImpl;
import io.airbyte.workers.temporal.spec.SpecWorkflowImpl;
import io.airbyte.workers.temporal.sync.SyncWorkflowImpl;
import io.grpc.StatusRuntimeException;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.micronaut.context.env.Environment;
import io.micronaut.context.event.ApplicationEventListener;
import io.micronaut.discovery.event.ServiceReadyEvent;
import io.micronaut.scheduling.TaskExecutors;
import io.temporal.api.workflowservice.v1.DescribeNamespaceRequest;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.worker.Worker;
import io.temporal.worker.WorkerFactory;
import io.temporal.worker.WorkerOptions;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import javax.inject.Inject;
import javax.inject.Named;
import javax.inject.Singleton;
import lombok.extern.slf4j.Slf4j;

/**
 * Performs any required initialization logic on application context start.
 */
@Singleton
@Requires(notEnv = {Environment.TEST})
@Slf4j
public class ApplicationInitializer implements ApplicationEventListener<ServiceReadyEvent> {

  @Value("${airbyte.role}")
  private String airbyteRole;
  @Inject
  private AirbyteVersion airbyteVersion;
  @Inject
  @Named("checkConnectionActivities")
  private List<Object> checkConnectionActivities;
  @Inject
  @Named("configsDatabaseMigrationCheck")
  private DatabaseMigrationCheck configsDatabaseMigrationCheck;
  @Inject
  private ConfigRepository configRepository;
  @Inject
  @Named("connectionManagerActivities")
  private List<Object> connectionManagerActivities;
  @Inject
  private DeploymentMode deploymentMode;
  @Inject
  @Named("discoverActivities")
  private List<Object> discoverActivities;
  @Inject
  @Named(TaskExecutors.IO)
  private ExecutorService executorService;
  @Inject
  @Named("jobsDatabaseMigrationCheck")
  private DatabaseMigrationCheck jobsDatabaseMigrationCheck;
  @Inject
  @Named("jobsDatabaseAvailabilityCheck")
  private JobsDatabaseAvailabilityCheck jobsDatabaseAvailabilityCheck;
  @Inject
  private JobPersistence jobPersistence;
  @Inject
  private LogConfigs logConfigs;
  @Value("${airbyte.worker.check.max-workers}")
  private Integer maxCheckWorkers;
  @Value("${airbyte.worker.discover.max-workers}")
  private Integer maxDiscoverWorkers;
  @Value("${airbyte.worker.spec.max-workers}")
  private Integer maxSpecWorkers;
  @Value("${airbyte.worker.sync.max-workers}")
  private Integer maxSyncWorkers;
  @Value("${airbyte.worker.check.enabled}")
  private boolean shouldRunCheckConnectionWorkflows;
  @Value("${airbyte.worker.connection.enabled}")
  private boolean shouldRunConnectionManagerWorkflows;
  @Value("${airbyte.worker.discover.enabled}")
  private boolean shouldRunDiscoverWorkflows;
  @Value("${airbyte.worker.spec.enabled}")
  private boolean shouldRunGetSpecWorkflows;
  @Value("${airbyte.worker.sync.enabled}")
  private boolean shouldRunSyncWorkflows;
  @Inject
  @Named("specActivities")
  private List<Object> specActivities;
  @Inject
  @Named("syncActivities")
  private List<Object> syncActivities;
  @Inject
  private TemporalProxyHelper temporalProxyHelper;
  @Inject
  private WorkflowServiceStubs temporalService;
  @Inject
  private TemporalUtils temporalUtils;
  @Value("${airbyte.temporal.worker.ports}")
  private Set<Integer> temporalWorkerPorts;
  @Inject
  private TrackingStrategy trackingStrategy;
  @Inject
  private WorkerEnvironment workerEnvironment;
  @Inject
  private WorkerFactory workerFactory;
  @Inject
  private WorkerPlane workerPlane;
  @Value("${airbyte.workspace.root}")
  private String workspaceRoot;

  @Override
  public void onApplicationEvent(final ServiceReadyEvent event) {
    try {
      initializeCommonDependencies();

      if (WorkerPlane.CONTROL_PLANE.equals(workerPlane)) {
        initializeControlPlaneDependencies();
      } else {
        log.info("Skipping Control Plane dependency initialization.");
      }

      log.info("Application initialized.");
    } catch (final DatabaseCheckException | ExecutionException | InterruptedException | IOException | TimeoutException e) {
      log.error("Unable to initialize application.", e);
      throw new IllegalStateException(e);
    }
  }

  private void initializeCommonDependencies() throws ExecutionException, InterruptedException, TimeoutException {
    log.info("Initializing common worker dependencies.");

    // Initialize the metric client
    MetricClientFactory.initialize(MetricEmittingApps.WORKER);

    // Configure logging client
    LogClientSingleton.getInstance().setWorkspaceMdc(workerEnvironment, logConfigs,
        LogClientSingleton.getInstance().getSchedulerLogsRoot(Path.of(workspaceRoot)));

    if (WorkerEnvironment.KUBERNETES.equals(workerEnvironment)) {
      KubePortManagerSingleton.init(temporalWorkerPorts);
    }

    configureTemporal(temporalUtils, temporalService);
  }

  private void initializeControlPlaneDependencies() throws DatabaseCheckException, IOException {
    // Ensure that the Configuration database has been migrated to the latest version
    log.info("Checking config database flyway migration version...");
    configsDatabaseMigrationCheck.check();

    // Ensure that the Jobs database has been migrated to the latest version
    log.info("Checking jobs database flyway migration version...");
    jobsDatabaseMigrationCheck.check();

    // Ensure that the Jobs database is available
    log.info("Checking jobs database availability...");
    jobsDatabaseAvailabilityCheck.check();

    TrackingClientSingleton.initialize(
        trackingStrategy,
        new Deployment(deploymentMode, jobPersistence.getDeployment().orElseThrow(),
            workerEnvironment),
        airbyteRole,
        airbyteVersion,
        configRepository);

    registerWorkerFactory(workerFactory, new MaxWorkersConfig(maxCheckWorkers, maxDiscoverWorkers, maxSpecWorkers, maxSyncWorkers));

    log.info("Starting worker factory...");
    workerFactory.start();
  }

  private void registerWorkerFactory(final WorkerFactory workerFactory, final MaxWorkersConfig maxWorkersConfiguration) {
    log.info("Registering worker factories....");
    if (shouldRunGetSpecWorkflows) {
      registerGetSpec(workerFactory, maxWorkersConfiguration);
    }

    if (shouldRunCheckConnectionWorkflows) {
      registerCheckConnection(workerFactory, maxWorkersConfiguration);
    }

    if (shouldRunDiscoverWorkflows) {
      registerDiscover(workerFactory, maxWorkersConfiguration);
    }

    if (shouldRunSyncWorkflows) {
      registerSync(workerFactory, maxWorkersConfiguration);
    }

    if (shouldRunConnectionManagerWorkflows) {
      registerConnectionManager(workerFactory, maxWorkersConfiguration);
    }
  }

  private void registerCheckConnection(final WorkerFactory factory, final MaxWorkersConfig maxWorkersConfig) {
    final Worker checkConnectionWorker =
        factory.newWorker(TemporalJobType.CHECK_CONNECTION.name(), getWorkerOptions(maxWorkersConfig.getMaxCheckWorkers()));
    checkConnectionWorker
        .registerWorkflowImplementationTypes(temporalProxyHelper.proxyWorkflowClass(CheckConnectionWorkflowImpl.class));
    checkConnectionWorker.registerActivitiesImplementations(checkConnectionActivities.toArray(new Object[] {}));
  }

  private void registerConnectionManager(final WorkerFactory factory, final MaxWorkersConfig maxWorkersConfig) {
    final Worker connectionUpdaterWorker =
        factory.newWorker(TemporalJobType.CONNECTION_UPDATER.toString(), getWorkerOptions(maxWorkersConfig.getMaxSyncWorkers()));
    connectionUpdaterWorker
        .registerWorkflowImplementationTypes(temporalProxyHelper.proxyWorkflowClass(ConnectionManagerWorkflowImpl.class));
    connectionUpdaterWorker.registerActivitiesImplementations(connectionManagerActivities.toArray(new Object[] {}));
  }

  private void registerDiscover(final WorkerFactory factory, final MaxWorkersConfig maxWorkersConfig) {
    final Worker discoverWorker =
        factory.newWorker(TemporalJobType.DISCOVER_SCHEMA.name(), getWorkerOptions(maxWorkersConfig.getMaxDiscoverWorkers()));
    discoverWorker
        .registerWorkflowImplementationTypes(temporalProxyHelper.proxyWorkflowClass(DiscoverCatalogWorkflowImpl.class));
    discoverWorker.registerActivitiesImplementations(discoverActivities.toArray(new Object[] {}));
  }

  private void registerGetSpec(final WorkerFactory factory, final MaxWorkersConfig maxWorkersConfig) {
    final Worker specWorker = factory.newWorker(TemporalJobType.GET_SPEC.name(), getWorkerOptions(maxWorkersConfig.getMaxSpecWorkers()));
    specWorker.registerWorkflowImplementationTypes(temporalProxyHelper.proxyWorkflowClass(SpecWorkflowImpl.class));
    specWorker.registerActivitiesImplementations(specActivities.toArray(new Object[] {}));
  }

  private void registerSync(final WorkerFactory factory, final MaxWorkersConfig maxWorkersConfig) {
    final Worker syncWorker = factory.newWorker(TemporalJobType.SYNC.name(), getWorkerOptions(maxWorkersConfig.getMaxSyncWorkers()));
    syncWorker.registerWorkflowImplementationTypes(temporalProxyHelper.proxyWorkflowClass(SyncWorkflowImpl.class));
    syncWorker.registerActivitiesImplementations(syncActivities.toArray(new Object[] {}));
  }

  private WorkerOptions getWorkerOptions(final int max) {
    return WorkerOptions.newBuilder()
        .setMaxConcurrentActivityExecutionSize(max)
        .build();
  }

  /**
   * Performs additional configuration of the Temporal service/connection.
   *
   * @param temporalUtils A {@link TemporalUtils} instance.
   * @param temporalService A {@link WorkflowServiceStubs} instance.
   * @throws ExecutionException if unable to perform the additional configuration.
   * @throws InterruptedException if unable to perform the additional configuration.
   * @throws TimeoutException if unable to perform the additional configuration.
   */
  private void configureTemporal(final TemporalUtils temporalUtils, final WorkflowServiceStubs temporalService)
      throws ExecutionException, InterruptedException, TimeoutException {
    log.info("Configuring Temporal....");
    // Create the default Temporal namespace
    temporalUtils.configureTemporalNamespace(temporalService);

    // Ensure that the Temporal namespace exists before continuing.
    // If it does not exist after 30 seconds, fail the startup.
    executorService.submit(this::waitForTemporalNamespace).get(30, TimeUnit.SECONDS);
  }

  /**
   * Blocks until the Temporal {@link TemporalUtils#DEFAULT_NAMESPACE} has been created. This is
   * necessary to avoid issues related to
   * https://community.temporal.io/t/running-into-an-issue-when-creating-namespace-programmatically/2783/8.
   */
  private void waitForTemporalNamespace() {
    boolean namespaceExists = false;
    while (!namespaceExists) {
      try {
        temporalService.blockingStub().describeNamespace(DescribeNamespaceRequest.newBuilder().setNamespace(TemporalUtils.DEFAULT_NAMESPACE).build());
        namespaceExists = true;
        // This is to allow the configured namespace to be available in the Temporal
        // cache before continuing on with any additional configuration/bean creation.
        Thread.sleep(TimeUnit.SECONDS.toMillis(5));
      } catch (final StatusRuntimeException e) {
        log.debug("Namespace '{}' does not exist yet.  Re-checking...", TemporalUtils.DEFAULT_NAMESPACE);
      } catch (final InterruptedException e) {
        log.debug("Sleep interrupted.  Exiting loop...");
      }
    }
  }

}
