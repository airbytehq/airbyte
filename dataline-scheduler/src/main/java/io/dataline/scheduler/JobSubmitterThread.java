package io.dataline.scheduler;

import com.google.common.collect.Sets;
import io.dataline.api.model.ConnectionRead;
import io.dataline.api.model.ConnectionSchedule;
import io.dataline.api.model.ConnectionStatus;
import io.dataline.api.model.Job;
import io.dataline.db.DatabaseHelper;
import io.dataline.workers.testing.EchoWorker;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Record;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;

// todo: have discovery and oneoffs be blocking (how to handle logs)
// todo: make endpoints in the API for reading job state
public class JobSubmitterThread implements Runnable {
  private static final Logger LOGGER = LoggerFactory.getLogger(JobSubmitterThread.class);

  private final ExecutorService threadPool;
  private final BasicDataSource connectionPool;

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
                    Optional<Record> jobEntryOptional =
                        ctx
                            .fetch(
                                "SELECT * FROM jobs WHERE scope = ? AND CAST(status AS VARCHAR) <> ? ORDER BY created_at DESC LIMIT 1",
                                connection.getConnectionId().toString(),
                                Job.StatusEnum.CANCELLED.toString().toLowerCase())
                            .stream()
                            .findFirst();

                    if (jobEntryOptional.isPresent()) {
                      Record jobEntry = jobEntryOptional.get();
                      Job job = new Job();
                      job.setId(jobEntry.getValue("id", Long.class));
                      job.setConnection(connection);
                      job.setCreatedAt(
                          jobEntry
                              .getValue("created_at", LocalDateTime.class)
                              .toEpochSecond(ZoneOffset.UTC));
                      job.setStartedAt(
                          jobEntry
                              .getValue("started_at", LocalDateTime.class)
                              .toEpochSecond(ZoneOffset.UTC));
                      job.setStatus(
                          Job.StatusEnum.fromValue(jobEntry.getValue("status", String.class)));
                      job.setUpdatedAt(
                          jobEntry
                              .getValue("updated_at", LocalDateTime.class)
                              .toEpochSecond(ZoneOffset.UTC));
                      return Optional.of(job);
                    } else {
                      return Optional.empty();
                    }
                  });

          if (lastJob.isEmpty()) {
            LOGGER.info("creating pending job for empty last job...");
            createPendingJob(connectionPool, connection.getConnectionId(), "{}");
            LOGGER.info("created pending job for empty last job...");
          } else {
            Job job = lastJob.get();

            switch (job.getStatus()) {
              case COMPLETED:
                ConnectionSchedule schedule = connection.getSchedule();
                long nextRunStart = job.getUpdatedAt() + getIntervalInSeconds(schedule);
                if (nextRunStart < Instant.now().getEpochSecond()) {
                  createPendingJob(connectionPool, job.getConnection().getConnectionId(), "{}");
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

  private static void createPendingJob(
      BasicDataSource connectionPool, UUID connectionId, String configJson) {
    LOGGER.info("Creating pending job for connection: " + connectionId.toString());
    LocalDateTime now = LocalDateTime.ofInstant(Instant.now(), ZoneOffset.UTC);
    try {
      DatabaseHelper.query(
          connectionPool,
          ctx ->
              ctx.execute(
                  "INSERT INTO jobs VALUES(DEFAULT, ?, ?, ?, ?, CAST(? AS JOB_STATUS), CAST(? as JSONB), ?, ?, ?)",
                  connectionId.toString(),
                  now,
                  now,
                  now,
                  Job.StatusEnum.PENDING.toString(),
                  configJson,
                  null, // todo: output
                  "", // todo: assign stdout
                  "") // todo: assign stderr
          );
    } catch (SQLException e) {
      LOGGER.error("sql", e);
      e.printStackTrace();
    }
  }

  private static Long getSecondsInUnit(ConnectionSchedule.TimeUnitEnum timeUnitEnum) {
    switch (timeUnitEnum) {
      case MINUTES:
        return TimeUnit.MINUTES.toSeconds(1);
      case HOURS:
        return TimeUnit.HOURS.toSeconds(1);
      case DAYS:
        return TimeUnit.DAYS.toSeconds(1);
      case WEEKS:
        return TimeUnit.DAYS.toSeconds(1) * 7;
      case MONTHS:
        return TimeUnit.DAYS.toSeconds(1) * 30;
      default:
        throw new RuntimeException("unhandled enum time unit: " + timeUnitEnum); // todo: assert in test to catch at build time
    }
  }

  private static Long getIntervalInSeconds(ConnectionSchedule schedule) {
    return getSecondsInUnit(schedule.getTimeUnit()) * schedule.getUnits().longValue();
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
}
