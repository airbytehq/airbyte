package io.dataline.scheduler;

import com.google.common.collect.Sets;
import com.google.common.util.concurrent.ThreadFactoryBuilder;
import io.dataline.api.model.ConnectionRead;
import io.dataline.api.model.ConnectionSchedule;
import io.dataline.api.model.ConnectionStatus;
import io.dataline.api.model.Job;
import io.dataline.db.DatabaseHelper;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.Worker;
import io.dataline.workers.WorkerStatus;
import java.math.BigDecimal;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// todo: add comment blurb to describe purpose of this class
public class Scheduler {
  private static final Logger LOGGER = LoggerFactory.getLogger(Scheduler.class);

  private static final int MAX_WORKERS = 4;
  private static final int JOB_SUBMITTER_THREAD = 1;
  private static final int MAX_THREADS = MAX_WORKERS + JOB_SUBMITTER_THREAD;
  private static final ThreadFactory THREAD_FACTORY =
      new ThreadFactoryBuilder().setNameFormat("scheduler-%d").build();

  // todo: make endpoints in the API for reading job state

  public Scheduler() {}

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

  // todo: provide blocking worker execution

  private static class EchoWorker implements Worker<String> {
    public EchoWorker() {}

    @Override
    public OutputAndStatus<String> run() {
      LOGGER.info("Hello World");
      return new OutputAndStatus<>("echoed", WorkerStatus.COMPLETED);
    }

    @Override
    public void cancel() {
      // no-op
    }
  }

  // todo: test constructing this
  private static class WorkerWrapper<T> implements Runnable {
    private final long jobId;
    private final Worker<T> worker;

    public WorkerWrapper(long jobId, Worker<T> worker) {
      this.jobId = jobId;
      this.worker = worker;
    }

    @Override
    public void run() {
      LOGGER.info("executing worker wrapper...");
      try {
        setJobStatus(jobId, Job.StatusEnum.RUNNING);
        // todo: use attempt here

        OutputAndStatus<T> outputAndStatus = worker.run();

        switch (outputAndStatus.status) {
          case CANCELLED:
            setJobStatus(jobId, Job.StatusEnum.CANCELLED);
            break;
          case FAILED:
            setJobStatus(jobId, Job.StatusEnum.FAILED);
            break;
          case COMPLETED:
            setJobStatus(jobId, Job.StatusEnum.COMPLETED);
            break;
        }

        // todo: propagate output
        LOGGER.info("output " + outputAndStatus.output.toString());
      } catch (Exception e) {
        LOGGER.error("worker error", e);
        setJobStatus(jobId, Job.StatusEnum.FAILED);
      }
    }
  }

  private static UUID CONNECTION_ID = UUID.randomUUID();

  private static Set<ConnectionRead> getAllActiveConnections() {
    // todo: get this from the api or a helper
    ConnectionSchedule testConnectionSchedule = new ConnectionSchedule();
    testConnectionSchedule.setUnits(new BigDecimal(1));
    testConnectionSchedule.setTimeUnit(ConnectionSchedule.TimeUnitEnum.MINUTES);

    ConnectionRead testConnection = new ConnectionRead();
    testConnection.setName("echo-connection");
    testConnection.setConnectionId(CONNECTION_ID);
    testConnection.setSourceImplementationId(UUID.randomUUID());
    testConnection.setDestinationImplementationId(UUID.randomUUID());
    testConnection.setSchedule(testConnectionSchedule);
    testConnection.setStatus(ConnectionStatus.ACTIVE);

    return Sets.newHashSet(testConnection);
  }

  private static void setJobStatus(long jobId, Job.StatusEnum status) {
    LOGGER.info("setting job status to " + status + " for job " + jobId);
    try {
      DatabaseHelper.execute(
          String.format("UPDATE jobs SET status = '%s' WHERE id = %d", status.toString(), jobId));
    } catch (SQLException e) {
      LOGGER.error("sql", e);
      throw new RuntimeException(e); // todo: actually handle this error
    }
  }

  // todo: have discovery and oneoffs be blocking (how to handle logs)

  private static class JobSubmitterThread implements Runnable {
    private final ExecutorService threadPool;

    public JobSubmitterThread(ExecutorService threadPool) {
      this.threadPool = threadPool;
    }

    @Override
    public void run() {
      try {
        while (true) {
          LOGGER.info("running job-submitter...");
          Set<ConnectionRead> activeConnections = getAllActiveConnections();
          for (ConnectionRead connection : activeConnections) {
            DatabaseHelper.executeQuery(
                "SELECT * FROM jobs",
                rs -> {
                  printResultSet("JOBS", rs);
                  return null;
                });

            Optional<Job> lastJob =
                DatabaseHelper.executeQuery(
                    String.format(
                        "SELECT * FROM jobs WHERE (connection_id = '%s' AND NOT status = 'cancelled') ORDER BY created_at DESC LIMIT 1",
                        connection.getConnectionId().toString()),
                    rs -> {
                      boolean hasJobEntry = rs.next();
                      if (hasJobEntry) {
                        Job job = new Job();
                        job.setId(rs.getLong("id"));
                        job.setConnection(connection);
                        job.setCreatedAt(rs.getLong("created_at"));
                        job.setStartedAt(rs.getLong("started_at"));
                        job.setStatus(Job.StatusEnum.fromValue(rs.getString("status")));
                        job.setUpdatedAt(rs.getLong("created_at"));

                        return Optional.of(job);
                      } else {
                        return Optional.empty();
                      }
                    });

            if (lastJob.isEmpty()) {
              LOGGER.info("creating pending job for empty last job...");
              createPendingJob(connection.getConnectionId());
              LOGGER.info("created pending job for empty last job...");
            } else {
              Job job = lastJob.get();

              switch (job.getStatus()) {
                case COMPLETED:
                  ConnectionSchedule schedule = connection.getSchedule();
                  long nextRunStart = job.getUpdatedAt() + getIntervalInSeconds(schedule);
                  if (nextRunStart < Instant.now().getEpochSecond()) {
                    createPendingJob(job.getConnection().getConnectionId());
                  }
                  break; // executes on next iteration
                case PENDING:
                case FAILED: // infinite retries for now
                  // todo: select kind of worker object to create
                  LOGGER.info("submitting job to thread pool...");
                  threadPool.submit(new WorkerWrapper<>(job.getId(), new EchoWorker()));
                case RUNNING:
                case CANCELLED:
                  //  no-op
                  break;
              }
            }
          }

          Thread.sleep(1000);
        }

      } catch (Throwable e) {
        LOGGER.error("sql", e);
      }
    }

    private static void printResultSet(String table, ResultSet rs) throws SQLException {
      System.out.println("ALL " + table + " START");
      ResultSetMetaData rsmd = rs.getMetaData();
      int columnsNumber = rsmd.getColumnCount();
      while (rs.next()) {
        for (int i = 1; i <= columnsNumber; i++) {
          if (i > 1) System.out.print(",  ");
          String columnValue = rs.getString(i);
          System.out.print(columnValue + " " + rsmd.getColumnName(i));
        }
        System.out.println("");
      }

      System.out.println("ALL " + table + " END");
    }

    private static void createPendingJob(UUID connectionId) {
      LOGGER.info("creating pending job for connection: " + connectionId.toString());
      long now = Instant.now().getEpochSecond();
      try {
        DatabaseHelper.execute(
            String.format(
                "INSERT INTO jobs VALUES (null, '%s', %d, %d, %d, '%s', '', '')",
                connectionId.toString(), now, now, now, Job.StatusEnum.PENDING.toString()));
      } catch (SQLException e) {
        LOGGER.error("sql", e);
        e.printStackTrace();
      }
    }

    // todo: align daily with calendar days, etc instead 24 hours after last run completion (drift
    // will be confusing)
    private static Long getIntervalInSeconds(ConnectionSchedule schedule) {
      switch (schedule.getTimeUnit()) {
        case MINUTES:
          return TimeUnit.MINUTES.toSeconds(1) * schedule.getUnits().longValue();
        case HOURS:
          return TimeUnit.HOURS.toSeconds(1) * schedule.getUnits().longValue();
        case DAYS:
          return TimeUnit.DAYS.toSeconds(1) * schedule.getUnits().longValue();
        case WEEKS:
          return TimeUnit.DAYS.toSeconds(1) * 7 * schedule.getUnits().longValue();
        case MONTHS:
          return TimeUnit.DAYS.toSeconds(1) * 30 * schedule.getUnits().longValue();
        default:
          throw new RuntimeException("unhandled enum time unit: " + schedule.getTimeUnit());
      }
    }
  }

  public void start() {
    ExecutorService threadPool = Executors.newFixedThreadPool(MAX_THREADS, THREAD_FACTORY);

    threadPool.submit(new JobSubmitterThread(threadPool));

    Runtime.getRuntime().addShutdownHook(new SchedulerShutdownHookThread(threadPool));
  }
}
