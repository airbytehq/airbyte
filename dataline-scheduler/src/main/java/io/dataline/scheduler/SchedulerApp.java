/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.scheduler;

import com.google.common.util.concurrent.ThreadFactoryBuilder;
import io.dataline.config.persistence.ConfigPersistence;
import io.dataline.config.persistence.DefaultConfigPersistence;
import io.dataline.db.DatabaseHelper;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;
import org.apache.commons.dbcp2.BasicDataSource;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * The SchedulerApp is responsible for finding new scheduled jobs that need to be run and to launch
 * them. The current implementation uses a thread pool on the scheduler's machine to launch the
 * jobs. One thread is reserved for the job submitter, which is responsible for finding and
 * launching new jobs.
 */
public class SchedulerApp {
  private static final Logger LOGGER = LoggerFactory.getLogger(SchedulerApp.class);

  private static final int MAX_WORKERS = 4;
  private static final long JOB_SUBMITTER_DELAY_MILLIS = 1000L;
  private static final ThreadFactory THREAD_FACTORY =
      new ThreadFactoryBuilder().setNameFormat("scheduler-%d").build();

  private final BasicDataSource connectionPool;
  private final String configPersistenceRoot;

  public SchedulerApp(BasicDataSource connectionPool, String configPersistenceRoot) {
    this.connectionPool = connectionPool;
    this.configPersistenceRoot = configPersistenceRoot;
  }

  public void start() {
    SchedulerPersistence schedulerPersistence = new DefaultSchedulerPersistence(connectionPool);
    ConfigPersistence configPersistence = new DefaultConfigPersistence(configPersistenceRoot);
    ExecutorService workerThreadPool = Executors.newFixedThreadPool(MAX_WORKERS, THREAD_FACTORY);
    ScheduledExecutorService scheduledPool = Executors.newSingleThreadScheduledExecutor();

    final JobSubmitter jobSubmitter =
        new JobSubmitter(workerThreadPool, connectionPool, schedulerPersistence);
    final JobScheduler jobScheduler =
        new JobScheduler(connectionPool, schedulerPersistence, configPersistence);

    scheduledPool.scheduleWithFixedDelay(
        new SchedulerAppInternal(jobScheduler, jobSubmitter),
        0L,
        JOB_SUBMITTER_DELAY_MILLIS,
        TimeUnit.MILLISECONDS);

    Runtime.getRuntime()
        .addShutdownHook(new SchedulerShutdownHandler(workerThreadPool, scheduledPool));
  }

  public static void main(String[] args) {
    final String configPersistenceRoot = System.getenv("CONFIG_PERSISTENCE_ROOT");
    LOGGER.info("configPersistenceRoot = " + configPersistenceRoot);

    LOGGER.info("Creating DB connection pool...");
    BasicDataSource connectionPool = DatabaseHelper.getConnectionPoolFromEnv();

    LOGGER.info("Launching scheduler...");
    new SchedulerApp(connectionPool, configPersistenceRoot).start();
  }
}
