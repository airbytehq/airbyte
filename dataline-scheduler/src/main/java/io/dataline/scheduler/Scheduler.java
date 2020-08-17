package io.dataline.scheduler;

import com.google.common.collect.Sets;
import com.google.common.util.concurrent.ThreadFactoryBuilder;
import io.dataline.api.model.ConnectionRead;
import io.dataline.api.model.ConnectionSchedule;
import io.dataline.api.model.ConnectionStatus;
import io.dataline.api.model.Job;
import io.dataline.db.DatabaseHelper;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.Worker;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.*;

import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Record;
import org.jooq.Result;
import org.jooq.Table;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import static org.jooq.impl.DSL.field;
import static org.jooq.impl.DSL.table;

// todo: handle the fact these arent connection ids anymore
// todo: split into separate files
// todo: add comment blurb to describe purpose of this class
public class Scheduler {
  private static final Logger LOGGER = LoggerFactory.getLogger(Scheduler.class);

  private static final int MAX_WORKERS = 4;
  private static final int JOB_SUBMITTER_THREAD = 1;
  private static final int MAX_THREADS = MAX_WORKERS + JOB_SUBMITTER_THREAD;
  private static final ThreadFactory THREAD_FACTORY =
      new ThreadFactoryBuilder().setNameFormat("scheduler-%d").build();
  private final BasicDataSource connectionPool;

  // todo: make endpoints in the API for reading job state

  public Scheduler(BasicDataSource connectionPool) {
    this.connectionPool = connectionPool;
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

  // todo: provide blocking worker execution

  private static class EchoWorker implements Worker<String> {
    public EchoWorker() {}

    @Override
    public OutputAndStatus<String> run() {
      LOGGER.info("Hello World");
      return new OutputAndStatus<>(JobStatus.SUCCESSFUL, "echoed");
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
    private BasicDataSource connectionPool;

    public WorkerWrapper(long jobId, Worker<T> worker, BasicDataSource connectionPool) {
      this.jobId = jobId;
      this.worker = worker;
      this.connectionPool = connectionPool;
    }

    @Override
    public void run() {
      LOGGER.info("executing worker wrapper...");
      try {
        setJobStatus(connectionPool, jobId, Job.StatusEnum.RUNNING);
        // todo: use attempt here

        OutputAndStatus<T> outputAndStatus = worker.run();

        switch (outputAndStatus.status) {
          case FAILED:
            setJobStatus(connectionPool, jobId, Job.StatusEnum.FAILED);
            break;
          case SUCCESSFUL:
            setJobStatus(connectionPool, jobId, Job.StatusEnum.COMPLETED);
            break;
        }

        // todo: propagate output
        LOGGER.info("output " + outputAndStatus.output.toString());
      } catch (Exception e) {
        LOGGER.error("worker error", e);
        setJobStatus(connectionPool, jobId, Job.StatusEnum.FAILED);
      }
    }
  }

  private static UUID CONNECTION_ID = UUID.randomUUID();

  private static Set<ConnectionRead> getAllActiveConnections() {
    // todo: get this from the api or a helper
    ConnectionSchedule testConnectionSchedule = new ConnectionSchedule();
    testConnectionSchedule.setUnits(1);
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

  private static void setJobStatus(
      BasicDataSource connectionPool, long jobId, Job.StatusEnum status) {
    LOGGER.info("setting job status to " + status + " for job " + jobId);
    try {
      DatabaseHelper.query(
          connectionPool,
          ctx -> {
            return ctx.update(table("jobs"))
                .set(field("status"), status.toString().toLowerCase())
                .where(field("id").eq(jobId))
                .execute();
          });
    } catch (SQLException e) {
      LOGGER.error("sql", e);
      throw new RuntimeException(e); // todo: actually handle this error
    }
  }

  // todo: have discovery and oneoffs be blocking (how to handle logs)

  private static class JobSubmitterThread implements Runnable {
    private final ExecutorService threadPool;
    private BasicDataSource connectionPool;

    public JobSubmitterThread(ExecutorService threadPool, BasicDataSource connectionPool) {
      this.threadPool = threadPool;
      this.connectionPool = connectionPool;
    }

    @Override
    public void run() {
      try {
        while (true) {
          LOGGER.info("running job-submitter...");
          Set<ConnectionRead> activeConnections = getAllActiveConnections();
          for (ConnectionRead connection : activeConnections) {
            Optional<Job> lastJob =
                DatabaseHelper.query(
                    connectionPool,
                    ctx -> {
                      ctx.resultQuery("", QueryPart)
                      Optional<Record> jobEntryOptional =
                          ctx
                              .select()
                              .from("jobs")
                              .where(field("scope").eq(connection.getConnectionId().toString()))
                              .and(field("status").notEqual("cancelled"))
                              .orderBy(field("created_at").desc())
                              .limit(1)
                              .fetch()
                              .stream()
                              .findFirst();

                      if (jobEntryOptional.isPresent()) {
                        Record jobEntry = jobEntryOptional.get();
                        Job job = new Job();
                        job.setId(jobEntry.getValue("id", Long.class));
                        job.setConnection(connection);
                        job.setCreatedAt(jobEntry.getValue("created_at", Long.class));
                        job.setStartedAt(jobEntry.getValue("started_at", Long.class));
                        job.setStatus(
                            Job.StatusEnum.fromValue(jobEntry.getValue("status", String.class)));
                        job.setUpdatedAt(jobEntry.getValue("updated_at", Long.class));
                        return Optional.of(job);
                      } else {
                        return Optional.empty();
                      }
                    });

            if (lastJob.isEmpty()) {
              LOGGER.info("creating pending job for empty last job...");
              createPendingJob(connectionPool, connection.getConnectionId());
              LOGGER.info("created pending job for empty last job...");
            } else {
              Job job = lastJob.get();

              switch (job.getStatus()) {
                case COMPLETED:
                  ConnectionSchedule schedule = connection.getSchedule();
                  long nextRunStart = job.getUpdatedAt() + getIntervalInSeconds(schedule);
                  if (nextRunStart < Instant.now().getEpochSecond()) {
                    createPendingJob(connectionPool, job.getConnection().getConnectionId());
                  }
                  break; // executes on next iteration
                case PENDING:
                case FAILED: // infinite retries for now
                  // todo: select kind of worker object to create
                  LOGGER.info("submitting job to thread pool...");
                  threadPool.submit(
                      new WorkerWrapper<>(job.getId(), new EchoWorker(), connectionPool));
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

    private static void createPendingJob(BasicDataSource connectionPool, UUID connectionId) {
      LOGGER.info("creating pending job for connection: " + connectionId.toString());
      long now = Instant.now().getEpochSecond();
      try {
        DatabaseHelper.query(
            connectionPool,
            ctx ->
                ctx.insertInto(table("jobs"))
                    .values(
                        null,
                        connectionId.toString(),
                        now,
                        now,
                        now,
                        Job.StatusEnum.PENDING.toString(),
                        "",
                        "")
                    .execute());
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

    threadPool.submit(new JobSubmitterThread(threadPool, connectionPool));

    Runtime.getRuntime().addShutdownHook(new SchedulerShutdownHookThread(threadPool));
  }
}
