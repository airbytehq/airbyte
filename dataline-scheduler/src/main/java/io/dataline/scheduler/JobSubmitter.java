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

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.dataline.api.model.ConnectionRead;
import io.dataline.api.model.ConnectionSchedule;
import io.dataline.db.DatabaseHelper;
import io.dataline.workers.singer.SingerTap;
import io.dataline.workers.singer.postgres_tap.SingerPostgresTapDiscoverWorker;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.HashSet;
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
  private final SchedulerPersistence persistence;

  public JobSubmitter(
      ExecutorService threadPool,
      BasicDataSource connectionPool,
      SchedulerPersistence persistence) {
    this.threadPool = threadPool;
    this.connectionPool = connectionPool;
    this.persistence = persistence;
  }

  @Override
  public void run() {
    try {
      LOGGER.info("Running job-submitter...");

      Optional<Job> oldestPendingJob = getOldestPendingJob();

      if (oldestPendingJob.isPresent()) {
        handleJob(oldestPendingJob.get());
      } else {
        handleScheduledJobs();
      }
    } catch (Throwable e) {
      LOGGER.error("Job Submitter Error", e);
    }
  }

  // todo: DRY this up
  private Optional<Job> getOldestPendingJob() throws SQLException {
    return DatabaseHelper.query(
        connectionPool,
        ctx -> {
          Optional<Record> jobEntryOptional =
              ctx
                  .fetch(
                      "SELECT * FROM jobs WHERE CAST(status AS VARCHAR) = 'pending' ORDER BY created_at ASC LIMIT 1")
                  .stream()
                  .findFirst();

          if (jobEntryOptional.isPresent()) {
            Record jobEntry = jobEntryOptional.get();
            Job job = DefaultSchedulerPersistence.getJobFromRecord(jobEntry);
            return Optional.of(job);
          } else {
            return Optional.empty();
          }
        });
  }

  private void handleScheduledJobs() throws SQLException {
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
                            JobStatus.CANCELLED.toString().toLowerCase())
                        .stream()
                        .findFirst();

                if (jobEntryOptional.isPresent()) {
                  Record jobEntry = jobEntryOptional.get();
                  Job job = DefaultSchedulerPersistence.getJobFromRecord(jobEntry);
                  return Optional.of(job);
                } else {
                  return Optional.empty();
                }
              });

      if (lastJob.isEmpty()) {
        createPendingJob(connectionPool, connection.getConnectionId().toString(), "{}");
      } else {
        Job job = lastJob.get();
        handleJob(job);
      }
    }
  }

  private void handleJob(Job job) {
    switch (job.getStatus()) {
      case CANCELLED:
      case COMPLETED:
        /*
        TODO: Need to handle getting the connection schedule for a sync.
        Maybe there's an easier way of adding a custom type like the EchoWorker
        ConnectionSchedule schedule = job.getConfig().getSync();
        long nextRunStart = job.getUpdatedAt() + getIntervalInSeconds(schedule);
        if (nextRunStart < Instant.now().getEpochSecond()) {
          createPendingJob(connectionPool, job);
        }
         */
        throw new RuntimeException("not implemented");
      case PENDING:
      case FAILED:
        switch (job.getConfig().getConfigType()) {
          case DISCOVER_SCHEMA:
            // todo: get tap from job's config
            SingerTap tap = SingerTap.POSTGRES;

            ObjectMapper objectMapper = new ObjectMapper();
            String configString = null;
            try {
              String rawConfigString =
                  objectMapper.writeValueAsString(job.getConfig().getDiscoverSchema());
              configString =
                  objectMapper.writeValueAsString(
                      objectMapper.readTree(rawConfigString).get("configuration"));

              LOGGER.info("config json: " + configString); // todo: remove
            } catch (IOException e) {
              throw new RuntimeException(e);
            }

            threadPool.submit(
                new WorkerWrapper<>(
                    job.getId(),
                    new SingerPostgresTapDiscoverWorker(),
                    connectionPool,
                    persistence));
            LOGGER.info("Submitting job to thread pool...");
            break;
          case CHECK_CONNECTION_SOURCE:
          case CHECK_CONNECTION_DESTINATION:
          case SYNC:
            throw new RuntimeException("not implemented");
            // todo: handle threadPool.submit(new WorkerWrapper<>(job.getId(), new EchoWorker(),
            // connectionPool));
        }
        break;
      case RUNNING:
        //  no-op
        break;
    }
  }

  private static void createPendingJob(
      BasicDataSource connectionPool, String scope, String jsonConfig) {
    try {
      LOGGER.info("Creating pending job for scope: " + scope);
      LocalDateTime now = LocalDateTime.ofInstant(Instant.now(), ZoneOffset.UTC);

      DatabaseHelper.query(
          connectionPool,
          ctx ->
              ctx.execute(
                  "INSERT INTO jobs VALUES(DEFAULT, ?, ?, ?, ?, CAST(? AS JOB_STATUS), CAST(? as JSONB), ?, ?, ?)",
                  scope,
                  now,
                  now,
                  now,
                  JobStatus.PENDING.toString().toLowerCase(),
                  jsonConfig,
                  null, // no output when created
                  JobLogs.getLogDirectory(scope),
                  JobLogs.getLogDirectory(scope)));
    } catch (SQLException e) {
      LOGGER.error("SQL Error", e);
      throw new RuntimeException(e);
    }
  }

  private static void createPendingJob(BasicDataSource connectionPool, Job previousJob) {
    try {
      createPendingJob(connectionPool, previousJob.getScope(), previousJob.getConfigAsJson());
    } catch (JsonProcessingException e) {
      throw new RuntimeException("JSON Error", e);
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
    //    TODO: re-enable test schedule
    //    ConnectionSchedule testConnectionSchedule = new ConnectionSchedule();
    //    testConnectionSchedule.setUnits(1l);
    //    testConnectionSchedule.setTimeUnit(ConnectionSchedule.TimeUnitEnum.MINUTES);
    //    ConnectionRead testConnection = new ConnectionRead();
    //    testConnection.setName("echo-connection");
    //    testConnection.setConnectionId(CONNECTION_ID);
    //    testConnection.setSourceImplementationId(UUID.randomUUID());
    //    testConnection.setDestinationImplementationId(UUID.randomUUID());
    //    testConnection.setSchedule(testConnectionSchedule);
    //    testConnection.setStatus(ConnectionStatus.ACTIVE);
    //
    //    return Sets.newHashSet(testConnection);

    return new HashSet<>();
  }
}
