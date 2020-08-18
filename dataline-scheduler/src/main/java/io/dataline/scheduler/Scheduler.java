package io.dataline.scheduler;

import com.google.common.util.concurrent.ThreadFactoryBuilder;
import java.util.concurrent.*;

import org.apache.commons.dbcp2.BasicDataSource;

/**
 * The Scheduler is responsible for finding new scheduled jobs that need to be run and to launch
 * them. The current implementation uses a thread pool on the scheduler's machine to launch the
 * jobs. One thread is reserved for the job submitter, which is responsible for finding and
 * launching new jobs.
 */
public class Scheduler {
  private static final int MAX_WORKERS = 4;
  private static final int JOB_SUBMITTER_THREAD = 1;
  private static final int MAX_THREADS = MAX_WORKERS + JOB_SUBMITTER_THREAD;
  private static final ThreadFactory THREAD_FACTORY =
      new ThreadFactoryBuilder().setNameFormat("scheduler-%d").build();

  private final BasicDataSource connectionPool;

  public Scheduler(BasicDataSource connectionPool) {
    this.connectionPool = connectionPool;
  }

  public void start() {
    ExecutorService threadPool = Executors.newFixedThreadPool(MAX_THREADS, THREAD_FACTORY);
    threadPool.submit(new JobSubmitterThread(threadPool, connectionPool));
    Runtime.getRuntime().addShutdownHook(new SchedulerShutdownThread(threadPool));
  }
}
