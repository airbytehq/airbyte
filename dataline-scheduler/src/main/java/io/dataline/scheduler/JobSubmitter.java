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

import com.google.common.collect.Sets;
import io.dataline.api.model.ConnectionRead;
import io.dataline.api.model.ConnectionSchedule;
import io.dataline.api.model.ConnectionStatus;
import io.dataline.api.model.Job;
import io.dataline.db.DatabaseHelper;
import io.dataline.workers.EchoWorker;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.TimeUnit;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Record;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class JobSubmitter implements Runnable {
  private static final Logger LOGGER = LoggerFactory.getLogger(JobSubmitter.class);

  private final ExecutorService threadPool;
  private final BasicDataSource connectionPool;

  public JobSubmitter(ExecutorService threadPool, BasicDataSource connectionPool) {
    this.threadPool = threadPool;
    this.connectionPool = connectionPool;
  }

  @Override
  public void run() {
    try {
      LOGGER.info("Running job-submitter...");

      // todo: get all pending jobs before considering configured connection schedules
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
                    job.setCreatedAt(getEpoch(jobEntry, "created_at"));
                    job.setStartedAt(getEpoch(jobEntry, "started_at"));
                    job.setStatus(
                        Job.StatusEnum.fromValue(jobEntry.getValue("status", String.class)));
                    job.setUpdatedAt(getEpoch(jobEntry, "updated_at"));
                    return Optional.of(job);
                  } else {
                    return Optional.empty();
                  }
                });

        if (lastJob.isEmpty()) {
          createPendingJob(connectionPool, connection.getConnectionId(), "{}");
        } else {
          Job job = lastJob.get();

          switch (job.getStatus()) {
            case CANCELLED:
            case COMPLETED:
              ConnectionSchedule schedule = connection.getSchedule();
              long nextRunStart = job.getUpdatedAt() + getIntervalInSeconds(schedule);
              if (nextRunStart < Instant.now().getEpochSecond()) {
                createPendingJob(connectionPool, job.getConnection().getConnectionId(), "{}");
              }
              break;
            case PENDING:
            case FAILED:
              // todo: Select kind of worker object to create based on the config
              LOGGER.info("Submitting job to thread pool...");
              threadPool.submit(new WorkerWrapper<>(job.getId(), new EchoWorker(), connectionPool));
            case RUNNING:
              //  no-op
              break;
          }
        }
      }
    } catch (Throwable e) {
      LOGGER.error("Job Submitter Error", e);
    }
  }

  private static long getEpoch(Record record, String fieldName) {
    return record.getValue(fieldName, LocalDateTime.class).toEpochSecond(ZoneOffset.UTC);
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
                  null,
                  JobLogs.getLogDirectory(connectionId.toString()),
                  JobLogs.getLogDirectory(connectionId.toString())));
    } catch (SQLException e) {
      LOGGER.error("SQL Error", e);
      e.printStackTrace();
    }
  }

  // todo: Assert in test to catch at build time
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
        throw new RuntimeException("Unhandled TimeUnitEnum: " + timeUnitEnum);
    }
  }

  private static Long getIntervalInSeconds(ConnectionSchedule schedule) {
    return getSecondsInUnit(schedule.getTimeUnit()) * schedule.getUnits().longValue();
  }

  private static UUID CONNECTION_ID = UUID.randomUUID();

  private static Set<ConnectionRead> getAllActiveConnections() {
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
