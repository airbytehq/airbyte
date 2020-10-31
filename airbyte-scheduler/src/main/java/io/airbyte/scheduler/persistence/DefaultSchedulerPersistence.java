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

package io.airbyte.scheduler.persistence;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnectionImplementation;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.SourceConnectionImplementation;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.db.Database;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import io.airbyte.scheduler.ScopeHelper;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.jooq.Record;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSchedulerPersistence implements SchedulerPersistence {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSchedulerPersistence.class);

  private final Database database;
  private final Supplier<Instant> timeSupplier;

  @VisibleForTesting
  DefaultSchedulerPersistence(Database database, Supplier<Instant> timeSupplier) {
    this.database = database;
    this.timeSupplier = timeSupplier;
  }

  public DefaultSchedulerPersistence(Database database) {
    this(database, Instant::now);
  }

  @Override
  public long createSourceCheckConnectionJob(SourceConnectionImplementation sourceImplementation, String dockerImageName) throws IOException {
    final String scope =
        ScopeHelper.createScope(
            JobConfig.ConfigType.CHECK_CONNECTION_SOURCE,
            sourceImplementation.getSourceImplementationId().toString());

    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(sourceImplementation.getConfiguration())
        .withDockerImage(dockerImageName);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.CHECK_CONNECTION_SOURCE)
        .withCheckConnection(jobCheckConnectionConfig);

    return createPendingJob(scope, jobConfig);
  }

  @Override
  public long createDestinationCheckConnectionJob(DestinationConnectionImplementation destinationImplementation, String dockerImageName)
      throws IOException {
    final String scope =
        ScopeHelper.createScope(
            JobConfig.ConfigType.CHECK_CONNECTION_DESTINATION,
            destinationImplementation.getDestinationImplementationId().toString());

    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(destinationImplementation.getConfiguration())
        .withDockerImage(dockerImageName);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.CHECK_CONNECTION_DESTINATION)
        .withCheckConnection(jobCheckConnectionConfig);

    return createPendingJob(scope, jobConfig);
  }

  @Override
  public long createDiscoverSchemaJob(SourceConnectionImplementation sourceImplementation, String dockerImageName) throws IOException {

    final String scope = ScopeHelper.createScope(
        JobConfig.ConfigType.DISCOVER_SCHEMA,
        sourceImplementation.getSourceImplementationId().toString());

    final JobDiscoverCatalogConfig jobDiscoverCatalogConfig = new JobDiscoverCatalogConfig()
        .withConnectionConfiguration(sourceImplementation.getConfiguration())
        .withDockerImage(dockerImageName);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.DISCOVER_SCHEMA)
        .withDiscoverCatalog(jobDiscoverCatalogConfig);

    return createPendingJob(scope, jobConfig);
  }

  @Override
  public long createGetSpecJob(String integrationImage) throws IOException {
    final String scope = ScopeHelper.createScope(
        JobConfig.ConfigType.GET_SPEC,
        integrationImage);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.GET_SPEC)
        .withGetSpec(new JobGetSpecConfig().withDockerImage(integrationImage));

    return createPendingJob(scope, jobConfig);
  }

  @Override
  public long createSyncJob(SourceConnectionImplementation sourceImplementation,
                            DestinationConnectionImplementation destinationImplementation,
                            StandardSync standardSync,
                            String sourceDockerImageName,
                            String destinationDockerImageName)
      throws IOException {
    final UUID connectionId = standardSync.getConnectionId();

    final String scope = ScopeHelper.createScope(JobConfig.ConfigType.SYNC, connectionId.toString());

    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withSourceConnectionImplementation(sourceImplementation)
        .withSourceDockerImage(sourceDockerImageName)
        .withDestinationConnectionImplementation(destinationImplementation)
        .withDestinationDockerImage(destinationDockerImageName)
        .withStandardSync(standardSync);

    final Optional<Job> previousJobOptional = getLastSyncJob(connectionId);
    final Optional<StandardSyncOutput> standardSyncOutput = previousJobOptional.flatMap(Job::getOutput).map(JobOutput::getSync);

    standardSyncOutput.map(StandardSyncOutput::getState).ifPresent(jobSyncConfig::withState);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.SYNC)
        .withSync(jobSyncConfig);
    return createPendingJob(scope, jobConfig);
  }

  // configJson is a oneOf checkConnection, discoverSchema, sync
  private long createPendingJob(String scope, JobConfig jobConfig) throws IOException {
    LOGGER.info("creating pending job for scope: " + scope);
    LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);

    try {
      final Record record = database.query(
          ctx -> ctx.fetch(
              "INSERT INTO jobs(scope, created_at, updated_at, status, config, output, attempts) VALUES(?, ?, ?, CAST(? AS JOB_STATUS), CAST(? as JSONB), ?, ?) RETURNING id",
              scope,
              now,
              now,
              JobStatus.PENDING.toString().toLowerCase(),
              Jsons.serialize(jobConfig),
              null,
              0))
          .stream()
          .findFirst()
          .orElseThrow(() -> new RuntimeException("This should not happen"));
      return record.getValue("id", Long.class);
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  @Override
  public void updateStatus(long jobId, JobStatus status) throws IOException {
    LOGGER.info("Setting job status to " + status + " for job " + jobId);
    LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);

    try {
      database.query(
          ctx -> ctx.execute(
              "UPDATE jobs SET status = CAST(? as JOB_STATUS), updated_at = ? WHERE id = ?",
              status.toString().toLowerCase(),
              now,
              jobId));
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  @Override
  public void updateLogPath(long jobId, Path logPath) throws IOException {
    LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);
    try {
      database.query(
          ctx -> ctx.execute(
              "UPDATE jobs SET log_path = ?, updated_at = ? WHERE id = ?",
              logPath.toString(),
              now,
              jobId));
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  @Override
  public void incrementAttempts(long jobId) throws IOException {
    try {
      database.query(
          ctx -> ctx.execute("UPDATE jobs SET attempts = attempts + 1 WHERE id = ?", jobId));
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  @Override
  public <T> void writeOutput(long jobId, T output) throws IOException {
    LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);

    try {
      database.query(
          ctx -> ctx.execute(
              "UPDATE jobs SET output = CAST(? as JSONB), updated_at = ? WHERE id = ?",
              Jsons.serialize(output),
              now,
              jobId));
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  @Override
  public Job getJob(long jobId) throws IOException {
    try {
      return database.query(
          ctx -> {
            Record jobEntry =
                ctx.fetch("SELECT * FROM jobs WHERE id = ?", jobId).stream()
                    .findFirst()
                    .orElseThrow(() -> new RuntimeException("Could not find job with id: " + jobId));

            return getJobFromRecord(jobEntry);
          });
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  @Override
  public List<Job> listJobs(JobConfig.ConfigType configType, String configId) throws IOException {
    try {
      String scope = ScopeHelper.createScope(configType, configId);
      return database.query(
          ctx -> ctx.fetch("SELECT * FROM jobs WHERE scope = ? ORDER BY created_at DESC", scope).stream()
              .map(DefaultSchedulerPersistence::getJobFromRecord)
              .collect(Collectors.toList()));
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  @Override
  public List<Job> listJobsWithStatus(JobConfig.ConfigType configType, JobStatus status) throws IOException {
    // todo (cgardens) - jooq does not let you use bindings to do LIKE queries. you have to construct
    // the string yourself or use their DSL.
    final String likeStatement = "'" + ScopeHelper.getScopePrefix(configType) + "%'";
    try {
      return database.query(
          ctx -> ctx
              .fetch("SELECT * FROM jobs WHERE scope LIKE " + likeStatement + " AND CAST(status AS VARCHAR) = ? ORDER BY created_at DESC",
                  status.toString().toLowerCase())
              .stream()
              .map(DefaultSchedulerPersistence::getJobFromRecord)
              .collect(Collectors.toList()));
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  @Override
  public Optional<Job> getLastSyncJob(UUID connectionId) throws IOException {
    try {
      return database.query(
          ctx -> {
            Optional<Record> jobEntryOptional =
                ctx
                    .fetch("SELECT * FROM jobs WHERE scope = ? AND CAST(status AS VARCHAR) <> ? ORDER BY created_at DESC LIMIT 1",
                        ScopeHelper.createScope(JobConfig.ConfigType.SYNC, connectionId.toString()),
                        JobStatus.CANCELLED.toString().toLowerCase())
                    .stream()
                    .findFirst();

            if (jobEntryOptional.isPresent()) {
              Record jobEntry = jobEntryOptional.get();
              Job job = getJobFromRecord(jobEntry);
              return Optional.of(job);
            } else {
              return Optional.empty();
            }
          });
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  @Override
  public Optional<Job> getOldestPendingJob() throws IOException {
    try {
      return database.query(
          ctx -> {
            Optional<Record> jobEntryOptional = ctx
                .fetch("SELECT * FROM jobs WHERE CAST(status AS VARCHAR) = 'pending' ORDER BY created_at ASC LIMIT 1")
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
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  // todo (cgardens) - the location of this method is a little weird. right now all of our db (and
  // record) interactions are confined to this class. would like to keep it that way for now, but
  // once we have other classes that interact with the db, this can be moved out.
  public static Job getJobFromRecord(Record jobEntry) {
    final JobConfig jobConfig = Jsons.deserialize(jobEntry.get("config", String.class), JobConfig.class);

    final String outputDb = jobEntry.get("output", String.class);
    final JobOutput output = outputDb == null ? null : Jsons.deserialize(outputDb, JobOutput.class);

    return new Job(
        jobEntry.get("id", Long.class),
        jobEntry.get("scope", String.class),
        jobConfig,
        jobEntry.get("log_path", String.class),
        output,
        jobEntry.get("attempts", Integer.class),
        JobStatus.valueOf(jobEntry.get("status", String.class).toUpperCase()),
        Optional.ofNullable(jobEntry.get("started_at")).map(value -> getEpoch(jobEntry, "started_at")).orElse(null),
        getEpoch(jobEntry, "created_at"),
        getEpoch(jobEntry, "updated_at"));
  }

  private static long getEpoch(Record record, String fieldName) {
    return record.get(fieldName, LocalDateTime.class).toEpochSecond(ZoneOffset.UTC);
  }

}
