/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.scheduler.app;

import com.google.common.util.concurrent.ThreadFactoryBuilder;
import io.airbyte.analytics.Deployment;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.ApiClient;
import io.airbyte.api.client.invoker.ApiException;
import io.airbyte.api.client.model.HealthCheckRead;
import io.airbyte.commons.concurrency.GracefulShutdownHandler;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.helpers.LogClientSingleton;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DatabaseConfigPersistence;
import io.airbyte.db.Database;
import io.airbyte.db.instance.configs.ConfigsDatabaseInstance;
import io.airbyte.db.instance.jobs.JobsDatabaseInstance;
import io.airbyte.scheduler.app.worker_run.TemporalWorkerRunFactory;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobNotifier;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker;
import io.airbyte.workers.temporal.TemporalClient;
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
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.slf4j.MDC;

/**
 * The SchedulerApp is responsible for finding new scheduled jobs that need to be run and to launch
 * them. The current implementation uses two thread pools to do so. One pool is responsible for all
 * job launching operations. The other pool is responsible for clean up operations.
 *
 * Operations can have thread pools under the hood. An important thread pool to note is that the job
 * submitter thread pool. This pool does the work of submitting jobs to temporal - the size of this
 * pool determines the number of concurrent jobs that can be run. This is controlled via the
 * {@link #SUBMITTER_NUM_THREADS} variable.
 */
public class SchedulerApp {

  private static final Logger LOGGER = LoggerFactory.getLogger(SchedulerApp.class);

  private static final long GRACEFUL_SHUTDOWN_SECONDS = 30;
  private static final int SUBMITTER_NUM_THREADS = Integer.parseInt(new EnvConfigs().getSubmitterNumThreads());
  private static final Duration SCHEDULING_DELAY = Duration.ofSeconds(5);
  private static final Duration CLEANING_DELAY = Duration.ofHours(2);
  private static final ThreadFactory THREAD_FACTORY = new ThreadFactoryBuilder().setNameFormat("worker-%d").build();

  private final Path workspaceRoot;
  private final JobPersistence jobPersistence;
  private final ConfigRepository configRepository;
  private final JobCleaner jobCleaner;
  private final JobNotifier jobNotifier;
  private final TemporalClient temporalClient;

  public SchedulerApp(Path workspaceRoot,
                      JobPersistence jobPersistence,
                      ConfigRepository configRepository,
                      JobCleaner jobCleaner,
                      JobNotifier jobNotifier,
                      TemporalClient temporalClient) {
    this.workspaceRoot = workspaceRoot;
    this.jobPersistence = jobPersistence;
    this.configRepository = configRepository;
    this.jobCleaner = jobCleaner;
    this.jobNotifier = jobNotifier;
    this.temporalClient = temporalClient;
  }

  public void start() throws IOException {
    final ExecutorService workerThreadPool = Executors.newFixedThreadPool(SUBMITTER_NUM_THREADS, THREAD_FACTORY);
    final ScheduledExecutorService scheduledPool = Executors.newSingleThreadScheduledExecutor();
    final TemporalWorkerRunFactory temporalWorkerRunFactory = new TemporalWorkerRunFactory(temporalClient, workspaceRoot);
    final JobRetrier jobRetrier = new JobRetrier(jobPersistence, Instant::now, jobNotifier);
    final JobScheduler jobScheduler = new JobScheduler(jobPersistence, configRepository);
    final JobSubmitter jobSubmitter = new JobSubmitter(
        workerThreadPool,
        jobPersistence,
        temporalWorkerRunFactory,
        new JobTracker(configRepository, jobPersistence),
        jobNotifier);

    Map<String, String> mdc = MDC.getCopyOfContextMap();

    // We cancel jobs that where running before the restart. They are not being monitored by the worker
    // anymore.
    cleanupZombies(jobPersistence, jobNotifier);

    scheduledPool.scheduleWithFixedDelay(
        () -> {
          MDC.setContextMap(mdc);
          jobRetrier.run();
          jobScheduler.run();
          jobSubmitter.run();
        },
        0L,
        SCHEDULING_DELAY.toSeconds(),
        TimeUnit.SECONDS);

    scheduledPool.scheduleWithFixedDelay(
        () -> {
          MDC.setContextMap(mdc);
          jobCleaner.run();
          jobPersistence.purgeJobHistory();
        },
        CLEANING_DELAY.toSeconds(),
        CLEANING_DELAY.toSeconds(),
        TimeUnit.SECONDS);

    Runtime.getRuntime().addShutdownHook(new GracefulShutdownHandler(Duration.ofSeconds(GRACEFUL_SHUTDOWN_SECONDS), workerThreadPool, scheduledPool));
  }

  private void cleanupZombies(JobPersistence jobPersistence, JobNotifier jobNotifier) throws IOException {
    for (Job zombieJob : jobPersistence.listJobsWithStatus(JobStatus.RUNNING)) {
      jobNotifier.failJob("zombie job was cancelled", zombieJob);
      jobPersistence.cancelJob(zombieJob.getId());
    }
  }

  public static void waitForServer(Configs configs) throws InterruptedException {
    final AirbyteApiClient apiClient = new AirbyteApiClient(
        new ApiClient().setScheme("http")
            .setHost(configs.getAirbyteApiHost())
            .setPort(configs.getAirbyteApiPort())
            .setBasePath("/api"));

    boolean isHealthy = false;
    while (!isHealthy) {
      try {
        HealthCheckRead healthCheck = apiClient.getHealthApi().getHealthCheck();
        isHealthy = healthCheck.getDb();
      } catch (ApiException e) {
        LOGGER.info("Waiting for server to become available...");
        Thread.sleep(2000);
      }
    }
  }

  public static void main(String[] args) throws IOException, InterruptedException {

    final Configs configs = new EnvConfigs();

    LogClientSingleton.setWorkspaceMdc(LogClientSingleton.getSchedulerLogsRoot(configs));

    final Path workspaceRoot = configs.getWorkspaceRoot();
    LOGGER.info("workspaceRoot = " + workspaceRoot);

    final String temporalHost = configs.getTemporalHost();
    LOGGER.info("temporalHost = " + temporalHost);

    // Wait for the server to initialize the database and run migration
    waitForServer(configs);

    LOGGER.info("Creating Job DB connection pool...");
    final Database jobDatabase = new JobsDatabaseInstance(
        configs.getDatabaseUser(),
        configs.getDatabasePassword(),
        configs.getDatabaseUrl())
            .getInitialized();

    final JobPersistence jobPersistence = new DefaultJobPersistence(jobDatabase);
    final Database configDatabase = new ConfigsDatabaseInstance(
        configs.getConfigDatabaseUser(),
        configs.getConfigDatabasePassword(),
        configs.getConfigDatabaseUrl())
            .getInitialized();
    final ConfigPersistence configPersistence = new DatabaseConfigPersistence(configDatabase).withValidation();
    final ConfigRepository configRepository = new ConfigRepository(configPersistence);
    final JobCleaner jobCleaner = new JobCleaner(
        configs.getWorkspaceRetentionConfig(),
        workspaceRoot,
        jobPersistence);
    final JobNotifier jobNotifier = new JobNotifier(configs.getWebappUrl(), configRepository, new WorkspaceHelper(configRepository, jobPersistence));

    AirbyteVersion.assertIsCompatible(configs.getAirbyteVersion(), jobPersistence.getVersion().get());

    TrackingClientSingleton.initialize(
        configs.getTrackingStrategy(),
        new Deployment(configs.getDeploymentMode(), jobPersistence.getDeployment().orElseThrow(), configs.getWorkerEnvironment()),
        configs.getAirbyteRole(),
        configs.getAirbyteVersion(),
        configRepository);

    final TemporalClient temporalClient = TemporalClient.production(temporalHost, workspaceRoot);

    LOGGER.info("Launching scheduler...");
    new SchedulerApp(workspaceRoot, jobPersistence, configRepository, jobCleaner, jobNotifier, temporalClient)
        .start();
  }

}
