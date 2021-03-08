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

package io.airbyte.scheduler;

import com.google.common.util.concurrent.ThreadFactoryBuilder;
import io.airbyte.analytics.TrackingClientSingleton;
import io.airbyte.commons.concurrency.GracefulShutdownHandler;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs;
import io.airbyte.config.EnvConfigs;
import io.airbyte.config.helpers.LogHelpers;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.config.persistence.DefaultConfigPersistence;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.scheduler.persistence.DefaultJobPersistence;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.temporal.TemporalClient;
import io.airbyte.scheduler.temporal.TemporalPool;
import io.airbyte.scheduler.temporal.TemporalUtils;
import io.airbyte.scheduler.temporal.TemporalWorkerRunFactory;
import io.airbyte.workers.process.DockerProcessBuilderFactory;
import io.airbyte.workers.process.KubeProcessBuilderFactory;
import io.airbyte.workers.process.ProcessBuilderFactory;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Duration;
import java.time.Instant;
import java.util.Map;
import java.util.Optional;
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
 * them. The current implementation uses a thread pool on the scheduler's machine to launch the
 * jobs. One thread is reserved for the job submitter, which is responsible for finding and
 * launching new jobs.
 */
public class SchedulerApp {

  private static final Logger LOGGER = LoggerFactory.getLogger(SchedulerApp.class);

  private static final long GRACEFUL_SHUTDOWN_SECONDS = 30;
  private static final int MAX_WORKERS = 4;
  private static final Duration SCHEDULING_DELAY = Duration.ofSeconds(5);
  private static final Duration CLEANING_DELAY = Duration.ofHours(2);
  private static final ThreadFactory THREAD_FACTORY = new ThreadFactoryBuilder().setNameFormat("worker-%d").build();

  private final Path workspaceRoot;
  private final ProcessBuilderFactory pbf;
  private final JobPersistence jobPersistence;
  private final ConfigRepository configRepository;
  private final JobCleaner jobCleaner;

  public SchedulerApp(Path workspaceRoot,
                      ProcessBuilderFactory pbf,
                      JobPersistence jobPersistence,
                      ConfigRepository configRepository,
                      JobCleaner jobCleaner) {
    this.workspaceRoot = workspaceRoot;
    this.pbf = pbf;
    this.jobPersistence = jobPersistence;
    this.configRepository = configRepository;
    this.jobCleaner = jobCleaner;
  }

  public void start() throws IOException {
    final TemporalPool temporalPool = new TemporalPool(workspaceRoot, pbf);
    // todo (cgardens) - i do not need to set up a thread pool for this, right?
    temporalPool.run();
    final TemporalClient temporalClient = new TemporalClient(TemporalUtils.TEMPORAL_CLIENT);

    final ExecutorService workerThreadPool = Executors.newFixedThreadPool(MAX_WORKERS, THREAD_FACTORY);
    final ScheduledExecutorService scheduledPool = Executors.newSingleThreadScheduledExecutor();
    final TemporalWorkerRunFactory temporalWorkerRunFactory = new TemporalWorkerRunFactory(temporalClient, workspaceRoot);
    final JobRetrier jobRetrier = new JobRetrier(jobPersistence, Instant::now);
    final JobScheduler jobScheduler = new JobScheduler(jobPersistence, configRepository);
    final JobSubmitter jobSubmitter = new JobSubmitter(
        workerThreadPool,
        jobPersistence,
        configRepository,
        temporalWorkerRunFactory);

    Map<String, String> mdc = MDC.getCopyOfContextMap();

    // We cancel jobs that where running before the restart. They are not being monitored by the worker
    // anymore.
    cleanupZombies(jobPersistence);

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
        },
        CLEANING_DELAY.toSeconds(),
        CLEANING_DELAY.toSeconds(),
        TimeUnit.SECONDS);

    Runtime.getRuntime().addShutdownHook(new GracefulShutdownHandler(Duration.ofSeconds(GRACEFUL_SHUTDOWN_SECONDS), workerThreadPool, scheduledPool));
  }

  private void cleanupZombies(JobPersistence jobPersistence) throws IOException {
    for (Job zombieJob : jobPersistence.listJobsWithStatus(JobStatus.RUNNING)) {
      jobPersistence.cancelJob(zombieJob.getId());
    }
  }

  private static ProcessBuilderFactory getProcessBuilderFactory(Configs configs) {
    if (configs.getWorkerEnvironment() == Configs.WorkerEnvironment.KUBERNETES) {
      return new KubeProcessBuilderFactory(configs.getWorkspaceRoot());
    } else {
      return new DockerProcessBuilderFactory(
          configs.getWorkspaceRoot(),
          configs.getWorkspaceDockerMount(),
          configs.getLocalDockerMount(),
          configs.getDockerNetwork());
    }
  }

  public static void main(String[] args) throws IOException, InterruptedException {

    final Configs configs = new EnvConfigs();

    final Path configRoot = configs.getConfigRoot();
    LOGGER.info("configRoot = " + configRoot);

    MDC.put(LogHelpers.WORKSPACE_MDC_KEY, LogHelpers.getSchedulerLogsRoot(configs).toString());

    final Path workspaceRoot = configs.getWorkspaceRoot();
    LOGGER.info("workspaceRoot = " + workspaceRoot);

    LOGGER.info("Creating DB connection pool...");
    final Database database = Databases.createPostgresDatabase(
        configs.getDatabaseUser(),
        configs.getDatabasePassword(),
        configs.getDatabaseUrl());

    final ProcessBuilderFactory pbf = getProcessBuilderFactory(configs);

    final JobPersistence jobPersistence = new DefaultJobPersistence(database);
    final ConfigPersistence configPersistence = new DefaultConfigPersistence(configRoot);
    final ConfigRepository configRepository = new ConfigRepository(configPersistence);
    final JobCleaner jobCleaner = new JobCleaner(
        configs.getWorkspaceRetentionConfig(),
        workspaceRoot,
        jobPersistence);

    TrackingClientSingleton.initialize(
        configs.getTrackingStrategy(),
        configs.getAirbyteRole(),
        configs.getAirbyteVersion(),
        configRepository);

    Optional<String> airbyteDatabaseVersion = jobPersistence.getVersion();
    int loopCount = 0;
    while (airbyteDatabaseVersion.isEmpty() && loopCount < 300) {
      LOGGER.warn("Waiting for Server to start...");
      TimeUnit.SECONDS.sleep(1);
      airbyteDatabaseVersion = jobPersistence.getVersion();
      loopCount++;
    }
    if (airbyteDatabaseVersion.isPresent()) {
      AirbyteVersion.assertIsCompatible(configs.getAirbyteVersion(), airbyteDatabaseVersion.get());
    } else {
      throw new IllegalStateException("Unable to retrieve Airbyte Version, aborting...");
    }

    LOGGER.info("Launching scheduler...");
    new SchedulerApp(workspaceRoot, pbf, jobPersistence, configRepository, jobCleaner).start();
  }

}
