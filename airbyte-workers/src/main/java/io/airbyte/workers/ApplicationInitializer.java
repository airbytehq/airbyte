/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers;

import datadog.trace.api.GlobalTracer;
import datadog.trace.api.Tracer;
import io.airbyte.commons.temporal.TemporalInitializationUtils;
import io.airbyte.commons.temporal.TemporalJobType;
import io.airbyte.commons.temporal.TemporalUtils;
import io.airbyte.commons.temporal.config.WorkerMode;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.MaxWorkersConfig;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.db.check.DatabaseCheckException;
import io.airbyte.db.check.DatabaseMigrationCheck;
import io.airbyte.db.check.impl.JobsDatabaseAvailabilityCheck;
import io.airbyte.metrics.lib.MetricClientFactory;
import io.airbyte.metrics.lib.MetricEmittingApps;
import io.airbyte.workers.process.KubePortManagerSingleton;
import io.airbyte.workers.temporal.check.connection.CheckConnectionWorkflowImpl;
import io.airbyte.workers.temporal.discover.catalog.DiscoverCatalogWorkflowImpl;
import io.airbyte.workers.temporal.scheduling.ConnectionManagerWorkflowImpl;
import io.airbyte.workers.temporal.scheduling.ConnectionNotificationWorkflowImpl;
import io.airbyte.workers.temporal.spec.SpecWorkflowImpl;
import io.airbyte.workers.temporal.support.TemporalProxyHelper;
import io.airbyte.workers.temporal.sync.SyncWorkflowImpl;
import io.airbyte.workers.tracing.StorageObjectGetInterceptor;
import io.airbyte.workers.tracing.TemporalSdkInterceptor;
import io.micronaut.context.annotation.Requires;
import io.micronaut.context.annotation.Value;
import io.micronaut.context.env.Environment;
import io.micronaut.context.event.ApplicationEventListener;
import io.micronaut.core.util.StringUtils;
import io.micronaut.discovery.event.ServiceReadyEvent;
import io.micronaut.scheduling.TaskExecutors;
import io.temporal.serviceclient.WorkflowServiceStubs;
import io.temporal.worker.NonDeterministicException;
import io.temporal.worker.Worker;
import io.temporal.worker.WorkerFactory;
import io.temporal.worker.WorkerOptions;
import io.temporal.worker.WorkflowImplementationOptions;
import jakarta.inject.Inject;
import jakarta.inject.Named;
import jakarta.inject.Singleton;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.stream.Collectors;
import lombok.extern.slf4j.Slf4j;

/**
 * Performs any required initialization logic on application context start.
 */
@Singleton
@Requires(notEnv = {Environment.TEST})
@Slf4j
public class ApplicationInitializer implements ApplicationEventListener<ServiceReadyEvent> {

  @Inject
  @Named("checkConnectionActivities")
  private Optional<List<Object>> checkConnectionActivities;
  @Inject
  @Named("configsDatabaseMigrationCheck")
  private Optional<DatabaseMigrationCheck> configsDatabaseMigrationCheck;
  @Inject
  @Named("connectionManagerActivities")
  private Optional<List<Object>> connectionManagerActivities;
  @Inject
  @Named("discoverActivities")
  private Optional<List<Object>> discoverActivities;

  @Inject
  @Named("notifyActivities")
  private Optional<List<Object>> notifyActivities;

  @Inject
  @Named(TaskExecutors.IO)
  private ExecutorService executorService;
  @Inject
  @Named("jobsDatabaseMigrationCheck")
  private Optional<DatabaseMigrationCheck> jobsDatabaseMigrationCheck;
  @Inject
  @Named("jobsDatabaseAvailabilityCheck")
  private Optional<JobsDatabaseAvailabilityCheck> jobsDatabaseAvailabilityCheck;

  @Inject
  private Optional<LogConfigs> logConfigs;
  @Value("${airbyte.worker.check.max-workers}")
  private Integer maxCheckWorkers;
  @Value("${airbyte.worker.notify.max-workers}")
  private Integer maxNotifyWorkers;
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
  @Value("${airbyte.worker.notify.enabled}")
  private boolean shouldRunNotifyWorkflows;

  @Inject
  @Named("specActivities")
  private Optional<List<Object>> specActivities;
  @Inject
  @Named("syncActivities")
  private Optional<List<Object>> syncActivities;
  @Inject
  private TemporalInitializationUtils temporalInitializationUtils;
  @Inject
  private TemporalProxyHelper temporalProxyHelper;
  @Inject
  private WorkflowServiceStubs temporalService;
  @Inject
  private TemporalUtils temporalUtils;
  @Value("${airbyte.temporal.worker.ports}")
  private Set<Integer> temporalWorkerPorts;
  @Inject
  private WorkerEnvironment workerEnvironment;
  @Inject
  private WorkerFactory workerFactory;
  @Value("${airbyte.workspace.root}")
  private String workspaceRoot;
  @Value("${airbyte.data.sync.task-queue}")
  private String syncTaskQueue;
  @Inject
  private Environment environment;

  @Override
  public void onApplicationEvent(final ServiceReadyEvent event) {
    try {
      configureTracer();
      initializeCommonDependencies();

      if (environment.getActiveNames().contains(WorkerMode.CONTROL_PLANE)) {
        initializeControlPlaneDependencies();
      } else {
        log.info("Skipping Control Plane dependency initialization.");
      }

      registerWorkerFactory(workerFactory,
          new MaxWorkersConfig(maxCheckWorkers, maxDiscoverWorkers, maxSpecWorkers,
              maxSyncWorkers, maxNotifyWorkers));

      log.info("Starting worker factory...");
      workerFactory.start();

      log.info("Application initialized.");
    } catch (final DatabaseCheckException | ExecutionException | InterruptedException | IOException | TimeoutException e) {
      log.error("Unable to initialize application.", e);
      throw new IllegalStateException(e);
    }
  }

  private void configureTracer() {
    final Tracer globalTracer = GlobalTracer.get();
    globalTracer.addTraceInterceptor(new StorageObjectGetInterceptor());
    globalTracer.addTraceInterceptor(new TemporalSdkInterceptor());
  }

  private void initializeCommonDependencies()
      throws ExecutionException, InterruptedException, TimeoutException {
    log.info("Initializing common worker dependencies.");

    // Initialize the metric client
    MetricClientFactory.initialize(MetricEmittingApps.WORKER);

    // Configure logging client
    LogClientSingleton.getInstance().setWorkspaceMdc(workerEnvironment, logConfigs.orElseThrow(),
        LogClientSingleton.getInstance().getSchedulerLogsRoot(Path.of(workspaceRoot)));

    if (environment.getActiveNames().contains(Environment.KUBERNETES)) {
      KubePortManagerSingleton.init(temporalWorkerPorts);
    }

    configureTemporal(temporalUtils, temporalService);
  }

  private void initializeControlPlaneDependencies() throws DatabaseCheckException, IOException {
    // Ensure that the Configuration database has been migrated to the latest version
    log.info("Checking config database flyway migration version...");
    configsDatabaseMigrationCheck.orElseThrow().check();

    // Ensure that the Jobs database has been migrated to the latest version
    log.info("Checking jobs database flyway migration version...");
    jobsDatabaseMigrationCheck.orElseThrow().check();

    // Ensure that the Jobs database is available
    log.info("Checking jobs database availability...");
    jobsDatabaseAvailabilityCheck.orElseThrow().check();
  }

  private void registerWorkerFactory(final WorkerFactory workerFactory,
                                     final MaxWorkersConfig maxWorkersConfiguration) {
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

    if (shouldRunNotifyWorkflows) {
      registerConnectionNotification(workerFactory, maxWorkersConfiguration);
    }
  }

  private void registerConnectionNotification(final WorkerFactory factory, final MaxWorkersConfig maxWorkersConfig) {
    final Worker notifyWorker = factory.newWorker(TemporalJobType.NOTIFY.name(), getWorkerOptions(maxWorkersConfig.getMaxNotifyWorkers()));
    final WorkflowImplementationOptions options =
        WorkflowImplementationOptions.newBuilder().setFailWorkflowExceptionTypes(NonDeterministicException.class).build();
    notifyWorker.registerWorkflowImplementationTypes(options, temporalProxyHelper.proxyWorkflowClass(ConnectionNotificationWorkflowImpl.class));
    notifyWorker.registerActivitiesImplementations(notifyActivities.orElseThrow().toArray(new Object[] {}));
  }

  private void registerCheckConnection(final WorkerFactory factory,
                                       final MaxWorkersConfig maxWorkersConfig) {
    final Worker checkConnectionWorker =
        factory.newWorker(TemporalJobType.CHECK_CONNECTION.name(),
            getWorkerOptions(maxWorkersConfig.getMaxCheckWorkers()));
    final WorkflowImplementationOptions options = WorkflowImplementationOptions.newBuilder()
        .setFailWorkflowExceptionTypes(NonDeterministicException.class).build();
    checkConnectionWorker
        .registerWorkflowImplementationTypes(options,
            temporalProxyHelper.proxyWorkflowClass(CheckConnectionWorkflowImpl.class));
    checkConnectionWorker.registerActivitiesImplementations(
        checkConnectionActivities.orElseThrow().toArray(new Object[] {}));
    log.info("Check Connection Workflow registered.");
  }

  private void registerConnectionManager(final WorkerFactory factory,
                                         final MaxWorkersConfig maxWorkersConfig) {
    final Worker connectionUpdaterWorker =
        factory.newWorker(TemporalJobType.CONNECTION_UPDATER.toString(),
            getWorkerOptions(maxWorkersConfig.getMaxSyncWorkers()));
    final WorkflowImplementationOptions options = WorkflowImplementationOptions.newBuilder()
        .setFailWorkflowExceptionTypes(NonDeterministicException.class).build();
    connectionUpdaterWorker
        .registerWorkflowImplementationTypes(options,
            temporalProxyHelper.proxyWorkflowClass(ConnectionManagerWorkflowImpl.class));
    connectionUpdaterWorker.registerActivitiesImplementations(
        connectionManagerActivities.orElseThrow().toArray(new Object[] {}));
    log.info("Connection Manager Workflow registered.");
  }

  private void registerDiscover(final WorkerFactory factory,
                                final MaxWorkersConfig maxWorkersConfig) {
    final Worker discoverWorker =
        factory.newWorker(TemporalJobType.DISCOVER_SCHEMA.name(),
            getWorkerOptions(maxWorkersConfig.getMaxDiscoverWorkers()));
    final WorkflowImplementationOptions options = WorkflowImplementationOptions.newBuilder()
        .setFailWorkflowExceptionTypes(NonDeterministicException.class).build();
    discoverWorker
        .registerWorkflowImplementationTypes(options,
            temporalProxyHelper.proxyWorkflowClass(DiscoverCatalogWorkflowImpl.class));
    discoverWorker.registerActivitiesImplementations(
        discoverActivities.orElseThrow().toArray(new Object[] {}));
    log.info("Discover Workflow registered.");
  }

  private void registerGetSpec(final WorkerFactory factory,
                               final MaxWorkersConfig maxWorkersConfig) {
    final Worker specWorker = factory.newWorker(TemporalJobType.GET_SPEC.name(),
        getWorkerOptions(maxWorkersConfig.getMaxSpecWorkers()));
    final WorkflowImplementationOptions options = WorkflowImplementationOptions.newBuilder()
        .setFailWorkflowExceptionTypes(NonDeterministicException.class).build();
    specWorker.registerWorkflowImplementationTypes(options,
        temporalProxyHelper.proxyWorkflowClass(SpecWorkflowImpl.class));
    specWorker.registerActivitiesImplementations(
        specActivities.orElseThrow().toArray(new Object[] {}));
    log.info("Get Spec Workflow registered.");
  }

  private void registerSync(final WorkerFactory factory, final MaxWorkersConfig maxWorkersConfig) {
    final Set<String> taskQueues = getSyncTaskQueue();

    // There should be a default value provided by the application framework. If not, do this
    // as a safety check to ensure we don't attempt to register against no task queue.
    if (taskQueues.isEmpty()) {
      throw new IllegalStateException("Sync workflow task queue must be provided.");
    }

    for (final String taskQueue : taskQueues) {
      log.info("Registering sync workflow for task queue '{}'...", taskQueue);
      final Worker syncWorker = factory.newWorker(taskQueue,
          getWorkerOptions(maxWorkersConfig.getMaxSyncWorkers()));
      final WorkflowImplementationOptions options = WorkflowImplementationOptions.newBuilder()
          .setFailWorkflowExceptionTypes(NonDeterministicException.class).build();
      syncWorker.registerWorkflowImplementationTypes(options,
          temporalProxyHelper.proxyWorkflowClass(SyncWorkflowImpl.class));
      syncWorker.registerActivitiesImplementations(
          syncActivities.orElseThrow().toArray(new Object[] {}));
    }
    log.info("Sync Workflow registered.");
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
  private void configureTemporal(final TemporalUtils temporalUtils,
                                 final WorkflowServiceStubs temporalService)
      throws ExecutionException, InterruptedException, TimeoutException {
    log.info("Configuring Temporal....");
    // Create the default Temporal namespace
    temporalUtils.configureTemporalNamespace(temporalService);

    // Ensure that the Temporal namespace exists before continuing.
    // If it does not exist after 30 seconds, fail the startup.
    executorService.submit(temporalInitializationUtils::waitForTemporalNamespace)
        .get(30, TimeUnit.SECONDS);
  }

  /**
   * Retrieve and parse the sync workflow task queue configuration.
   *
   * @return A set of Temporal task queues for the sync workflow.
   */
  private Set<String> getSyncTaskQueue() {
    if (StringUtils.isEmpty(syncTaskQueue)) {
      return Set.of();
    }
    return Arrays.stream(syncTaskQueue.split(",")).collect(Collectors.toSet());
  }

}
