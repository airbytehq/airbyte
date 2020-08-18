package io.dataline.scheduler;

import com.google.common.util.concurrent.ThreadFactoryBuilder;
import org.apache.commons.dbcp2.BasicDataSource;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ThreadFactory;
import java.util.concurrent.TimeUnit;

/**
 * The Scheduler is responsible for finding new scheduled jobs that need to be run and to launch
 * them. The current implementation uses a thread pool on the scheduler's machine to launch the
 * jobs. One thread is reserved for the job submitter, which is responsible for finding and
 * launching new jobs.
 */
public class Scheduler {
  private static final int MAX_WORKERS = 4;
  private static final long JOB_SUBMITTER_DELAY_MILLIS = 1000L;
  private static final ThreadFactory THREAD_FACTORY =
      new ThreadFactoryBuilder().setNameFormat("scheduler-%d").build();

  private final BasicDataSource connectionPool;

  public Scheduler(BasicDataSource connectionPool) {
    this.connectionPool = connectionPool;
  }

  public void start() {
    ExecutorService workerThreadPool = Executors.newFixedThreadPool(MAX_WORKERS, THREAD_FACTORY);
    ScheduledExecutorService scheduledPool = Executors.newSingleThreadScheduledExecutor();
    scheduledPool.scheduleWithFixedDelay(
        new JobSubmitter(workerThreadPool, connectionPool),
        0L,
        JOB_SUBMITTER_DELAY_MILLIS,
        TimeUnit.MILLISECONDS);

    Runtime.getRuntime()
        .addShutdownHook(new SchedulerShutdownHandler(workerThreadPool, scheduledPool));
  }
}
