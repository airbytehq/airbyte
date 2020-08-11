package io.dataline.scheduler;

import com.google.common.util.concurrent.ThreadFactoryBuilder;
import io.dataline.db.DatabaseHelper;
import java.sql.SQLException;
import java.util.concurrent.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// todo: add comment blurb to describe purpose of this class
public class Scheduler {
  private static final Logger LOGGER = LoggerFactory.getLogger(Scheduler.class);

  private static final int MAX_WORKERS = 4;
  private static final int JOB_SUBMITTER_THREADS = 1;
  private static final int JOB_CLEANUP_THREADS = 1;
  private static final int MAX_THREADS = MAX_WORKERS + JOB_SUBMITTER_THREADS + JOB_CLEANUP_THREADS;
  private static final ThreadFactory THREAD_FACTORY =
      new ThreadFactoryBuilder().setNameFormat("scheduler-%d").build();

  // todo: make endpoints in the API for reading job state

  public Scheduler() {}

  // todo: use a separate enum type for status so it generates nicely
  // todo: use format strings / unix timestamp in java
  public void updateJobStatus(long jobAttemptId, String status) throws SQLException {
    DatabaseHelper.execute(
        String.format(
            "UPDATE job_attempts SET (status = %s, updated_at = (SELECT strftime('%s', 'now'))) WHERE id = %d;",
            status, jobAttemptId));
  }

  public void heartbeat(long jobAttemptId) throws SQLException {
    DatabaseHelper.execute(
        String.format(
            "UPDATE job_attempts SET (last_heartbeat = (SELECT strftime('%s', 'now'))) WHERE id = %d;",
            jobAttemptId));
  }

  private static class SchedulerShutdownHookThread extends Thread {
    private ExecutorService threadPool;

    public SchedulerShutdownHookThread(ExecutorService threadPool) {
      this.threadPool = threadPool;
    }

    @Override
    public void run() {
      // todo: attempt graceful shutdown of workers

      threadPool.shutdown();

      try {
        if (!threadPool.awaitTermination(30, TimeUnit.SECONDS)) {
          LOGGER.error("Unable to kill worker threads by shutdown timeout.");
        }
      } catch (InterruptedException e) {
        LOGGER.error("Wait for graceful worker thread shutdown interrupted.", e);
      }
    }
  }

  private static class JobSubmitterThread implements Runnable {
    private final ExecutorService threadPool;
    private final int maxWorkers;

    public JobSubmitterThread(ExecutorService threadPool, int maxWorkers) {
      this.threadPool = threadPool;
      this.maxWorkers = maxWorkers;
    }

    @Override
    public void run() {
      // todo: retrieve list of scheduleimplementations + manual jobs and select one to process here
      // todo: create job and attempt in db
      // todo: submit appropriate worker thread
    }
  }

  private static class JobCleanupThread implements Runnable {
    private final ExecutorService threadPool;

    public JobCleanupThread(ExecutorService threadPool) {
      this.threadPool = threadPool;
    }

    @Override
    public void run() {
      // todo: implemement
    }
  }

  public void start() {
    ExecutorService threadPool = Executors.newFixedThreadPool(MAX_THREADS, THREAD_FACTORY);

    threadPool.submit(new JobSubmitterThread(threadPool, MAX_WORKERS));
    threadPool.submit(new JobCleanupThread(threadPool)); // todo: needs more than the thread pool

    Runtime.getRuntime().addShutdownHook(new SchedulerShutdownHookThread(threadPool));
  }
}
