/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.app;

import com.google.common.util.concurrent.ThreadFactoryBuilder;
import io.airbyte.analytics.Deployment;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.ApiClient;
import io.airbyte.api.client.invoker.ApiException;
import io.airbyte.api.client.model.HealthCheckRead;
import io.airbyte.commons.concurrency.GracefulShutdownHandler;
import io.airbyte.commons.features.EnvVariableFeatureFlags;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.lang.CloseableShutdownHook;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.config.persistence.split_secrets.JsonSecretsProcessor;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DSLContextFactory;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.metrics.lib.DatadogClientConfiguration;
import io.airbyte.metrics.lib.DogStatsDMetricSingleton;
import io.airbyte.metrics.lib.MetricEmittingApps;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.workers.WorkerConfigs;
import io.airbyte.workers.temporal.TemporalClient;
import io.airbyte.workers.worker_run.TemporalWorkerRunFactory;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

/**
 * The SchedulerApp is responsible for finding new scheduled jobs that need to be run and to launch
 * them. The current implementation uses two thread pools to do so. One pool is responsible for all
 * job launching operations. The other pool is responsible for clean up operations.
 * <p>
 * Operations can have thread pools under the hood. An important thread pool to note is that the job
 * submitter thread pool. This pool does the work of submitting jobs to temporal - the size of this
 * pool determines the number of concurrent jobs that can be run. This is controlled via the
 * SUBMITTER_NUM_THREADS variable of EnvConfigs.
 */
public class SchedulerApp {

  public static final AtomicInteger PENDING_JOBS = new AtomicInteger();

  private static final Logger LOGGER = LoggerFactory.getLogger(SchedulerApp.class);

  private static final long GRACEFUL_SHUTDOWN_SECONDS = 30;
  private static final Duration SCHEDULING_DELAY = Duration.ofSeconds(5);
  private static final Duration CLEANING_DELAY = Duration.ofHours(2);
  private static final ThreadFactory THREAD_FACTORY = new ThreadFactoryBuilder().setNameFormat("worker-%d").build();
  private static final String DRIVER_CLASS_NAME = "org.postgresql.Driver";

  private final Path workspaceRoot;
  private final JobPersistence jobPersistence;
  private final ConfigRepository configRepository;
  private final JobCleaner jobCleaner;
  private final JobNotifier jobNotifier;
  private final TemporalClient temporalClient;
  private final int submitterNumThreads;
  private final int maxSyncJobAttempts;
  private final String airbyteVersionOrWarnings;
  private final WorkerEnvironment workerEnvironment;
  private final LogConfigs logConfigs;

  public SchedulerApp(final Path workspaceRoot,
                      final JobPersistence jobPersistence,
                      final ConfigRepository configRepository,
                      final JobCleaner jobCleaner,
                      final JobNotifier jobNotifier,
                      final TemporalClient temporalClient,
                      final Integer submitterNumThreads,
                      final Integer maxSyncJobAttempts,
                      final String airbyteVersionOrWarnings,
                      final WorkerEnvironment workerEnvironment,
                      final LogConfigs logConfigs) {
    this.workspaceRoot = workspaceRoot;
    this.jobPersistence = jobPersistence;
    this.configRepository = configRepository;
    this.jobCleaner = jobCleaner;
    this.jobNotifier = jobNotifier;
    this.temporalClient = temporalClient;
    this.submitterNumThreads = submitterNumThreads;
    this.maxSyncJobAttempts = maxSyncJobAttempts;
    this.airbyteVersionOrWarnings = airbyteVersionOrWarnings;
    this.workerEnvironment = workerEnvironment;
    this.logConfigs = logConfigs;
  }

  public void start() throws IOException {
    final Configs configs = new EnvConfigs();
    final WorkerConfigs workerConfigs = new WorkerConfigs(configs);
    final FeatureFlags featureFlags = new EnvVariableFeatureFlags();
    if (!featureFlags.usesNewScheduler()) {
      final ExecutorService workerThreadPool = Executors.newFixedThreadPool(submitterNumThreads, THREAD_FACTORY);
      final ScheduledExecutorService scheduleJobsPool = Executors.newSingleThreadScheduledExecutor();
      final ScheduledExecutorService executeJobsPool = Executors.newSingleThreadScheduledExecutor();
      final ScheduledExecutorService cleanupJobsPool = Executors.newSingleThreadScheduledExecutor();
      final TemporalWorkerRunFactory temporalWorkerRunFactory = new TemporalWorkerRunFactory(
          temporalClient,
          workspaceRoot,
          airbyteVersionOrWarnings,
          featureFlags);
      final JobRetrier jobRetrier = new JobRetrier(jobPersistence, Instant::now, jobNotifier, maxSyncJobAttempts);
      final TrackingClient trackingClient = TrackingClientSingleton.get();
      final JobScheduler jobScheduler = new JobScheduler(
          configs.connectorSpecificResourceDefaultsEnabled(),
          jobPersistence,
          configRepository,
          trackingClient,
          workerConfigs);
      final JobSubmitter jobSubmitter = new JobSubmitter(
          workerThreadPool,
          jobPersistence,
          temporalWorkerRunFactory,
          new JobTracker(configRepository, jobPersistence, trackingClient),
          jobNotifier, workerEnvironment, logConfigs, configRepository);

      final Map<String, String> mdc = MDC.getCopyOfContextMap();

      // We cancel jobs that where running before the restart. They are not being monitored by the worker
      // anymore.
      cleanupZombies(jobPersistence, jobNotifier);

      LOGGER.info("Start running the old scheduler");
      scheduleJobsPool.scheduleWithFixedDelay(
          () -> {
            MDC.setContextMap(mdc);
            jobRetrier.run();
            jobScheduler.run();
          },
          0L,
          SCHEDULING_DELAY.toSeconds(),
          TimeUnit.SECONDS);

      executeJobsPool.scheduleWithFixedDelay(
          () -> {
            MDC.setContextMap(mdc);
            jobSubmitter.run();
          },
          0L,
          SCHEDULING_DELAY.toSeconds(),
          TimeUnit.SECONDS);

      cleanupJobsPool.scheduleWithFixedDelay(
          () -> {
            MDC.setContextMap(mdc);
            jobCleaner.run();
            jobPersistence.purgeJobHistory();
          },
          CLEANING_DELAY.toSeconds(),
          CLEANING_DELAY.toSeconds(),
          TimeUnit.SECONDS);

      Runtime.getRuntime().addShutdownHook(new GracefulShutdownHandler(Duration.ofSeconds(GRACEFUL_SHUTDOWN_SECONDS), workerThreadPool,
          scheduleJobsPool, executeJobsPool, cleanupJobsPool));
    }
  }

  private void cleanupZombies(final JobPersistence jobPersistence, final JobNotifier jobNotifier) throws IOException {
    for (final Job zombieJob : jobPersistence.listJobsWithStatus(JobStatus.RUNNING)) {
      jobNotifier.failJob("zombie job was failed", zombieJob);

      final int currentAttemptNumber = zombieJob.getAttemptsCount() - 1;

      LOGGER.warn(
          "zombie clean up - job attempt was failed. job id: {}, attempt number: {}, type: {}, scope: {}",
          zombieJob.getId(),
          currentAttemptNumber,
          zombieJob.getConfigType(),
          zombieJob.getScope());

      jobPersistence.failAttempt(
          zombieJob.getId(),
          currentAttemptNumber);
    }
  }

  public static void waitForServer(final Configs configs) throws InterruptedException {
    final AirbyteApiClient apiClient = new AirbyteApiClient(
        new ApiClient().setScheme("http")
            .setHost(configs.getAirbyteApiHost())
            .setPort(configs.getAirbyteApiPort())
            .setBasePath("/api"));

    boolean isHealthy = false;
    while (!isHealthy) {
      try {
        final HealthCheckRead healthCheck = apiClient.getHealthApi().getHealthCheck();
        isHealthy = healthCheck.getAvailable();
      } catch (final ApiException e) {
        LOGGER.info("Waiting for server to become available...");
        Thread.sleep(2000);
      }
    }
  }

  public static void main(final String[] args) throws IOException, InterruptedException {

    final Configs configs = new EnvConfigs();

    LogClientSingleton.getInstance().setWorkspaceMdc(configs.getWorkerEnvironment(), configs.getLogConfigs(),
        LogClientSingleton.getInstance().getSchedulerLogsRoot(configs.getWorkspaceRoot()));

    final Path workspaceRoot = configs.getWorkspaceRoot();
    LOGGER.info("workspaceRoot = " + workspaceRoot);

    final String temporalHost = configs.getTemporalHost();
    LOGGER.info("temporalHost = " + temporalHost);

    final DataSource configsDataSource = DataSourceFactory.create(configs.getConfigDatabaseUser(), configs.getConfigDatabasePassword(),
        DRIVER_CLASS_NAME, configs.getConfigDatabaseUrl());

    final DataSource jobsDataSource = DataSourceFactory.create(configs.getDatabaseUser(), configs.getDatabasePassword(),
        DRIVER_CLASS_NAME, configs.getDatabaseUrl());

    // Manual configuration that will be replaced by Dependency Injection in the future
    try (final DSLContext configsDslContext = DSLContextFactory.create(configsDataSource, SQLDialect.POSTGRES);
        final DSLContext jobsDslContext = DSLContextFactory.create(jobsDataSource, SQLDialect.POSTGRES)) {

      // Ensure that the database resources are closed on application shutdown
      CloseableShutdownHook.registerRuntimeShutdownHook(configsDataSource, jobsDataSource, configsDslContext, jobsDslContext);

      // Wait for the server to initialize the database and run migration
      // This should be converted into check for the migration version. Everything else as per.
      waitForServer(configs);
      LOGGER.info("Creating Job DB connection pool...");
      final Database jobDatabase = new JobsDatabaseInstance(jobsDslContext).getInitialized();

      final Database configDatabase = new ConfigsDatabaseInstance(configsDslContext).getInitialized();
      final FeatureFlags featureFlags = new EnvVariableFeatureFlags();
      final JsonSecretsProcessor jsonSecretsProcessor = JsonSecretsProcessor.builder()
          .maskSecrets(!featureFlags.exposeSecretsInExport())
          .copySecrets(true)
          .build();
      final ConfigPersistence configPersistence = DatabaseConfigPersistence.createWithValidation(configDatabase, jsonSecretsProcessor);
      final ConfigRepository configRepository = new ConfigRepository(configPersistence, configDatabase);

      final JobPersistence jobPersistence = new DefaultJobPersistence(jobDatabase);
      final JobCleaner jobCleaner = new JobCleaner(
          configs.getWorkspaceRetentionConfig(),
          workspaceRoot,
          jobPersistence);
      AirbyteVersion.assertIsCompatible(
          configs.getAirbyteVersion(),
          jobPersistence.getVersion().map(AirbyteVersion::new).orElseThrow());

      TrackingClientSingleton.initialize(
          configs.getTrackingStrategy(),
          new Deployment(configs.getDeploymentMode(), jobPersistence.getDeployment().orElseThrow(), configs.getWorkerEnvironment()),
          configs.getAirbyteRole(),
          configs.getAirbyteVersion(),
          configRepository);
      final JobNotifier jobNotifier = new JobNotifier(
          configs.getWebappUrl(),
          configRepository,
          new WorkspaceHelper(configRepository, jobPersistence),
          TrackingClientSingleton.get());
      final TemporalClient temporalClient = TemporalClient.production(temporalHost, workspaceRoot, configs);

      DogStatsDMetricSingleton.initialize(MetricEmittingApps.SCHEDULER, new DatadogClientConfiguration(configs));

      LOGGER.info("Launching scheduler...");
      new SchedulerApp(
          workspaceRoot,
          jobPersistence,
          configRepository,
          jobCleaner,
          jobNotifier,
          temporalClient,
          Integer.parseInt(configs.getSubmitterNumThreads()),
          configs.getSyncJobMaxAttempts(),
          configs.getAirbyteVersionOrWarning(), configs.getWorkerEnvironment(), configs.getLogConfigs())
              .start();
    }
  }

}
