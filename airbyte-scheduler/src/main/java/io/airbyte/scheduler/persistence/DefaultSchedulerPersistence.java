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
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.db.Database;
import io.airbyte.scheduler.Attempt;
import io.airbyte.scheduler.AttemptStatus;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import io.airbyte.scheduler.ScopeHelper;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.jooq.Record;
import org.jooq.Result;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSchedulerPersistence implements SchedulerPersistence {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSchedulerPersistence.class);
  @VisibleForTesting
  static final String BASE_JOB_SELECT_AND_JOIN =
      "SELECT\n"
          + "jobs.id AS job_id,\n"
          + "jobs.scope AS scope,\n"
          + "jobs.config AS config,\n"
          + "jobs.status AS job_status,\n"
          + "jobs.started_at AS job_started_at,\n"
          + "jobs.created_at AS job_created_at,\n"
          + "jobs.updated_at AS job_updated_at,\n"
          + "attempts.attempt_id AS attempt_id,\n"
          + "attempts.log_path AS log_path,\n"
          + "attempts.output AS attempt_output,\n"
          + "attempts.status AS attempt_status,\n"
          + "attempts.started_at AS attempt_started_at,\n"
          + "attempts.created_at AS attempt_created_at,\n"
          + "attempts.updated_at AS attempt_updated_at\n"
          + "FROM jobs LEFT OUTER JOIN attempts ON jobs.id = attempts.job_id ";

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
  public long createSourceCheckConnectionJob(SourceConnection source, String dockerImageName) throws IOException {
    final String scope =
        ScopeHelper.createScope(
            JobConfig.ConfigType.CHECK_CONNECTION_SOURCE,
            source.getSourceId().toString());

    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(source.getConfiguration())
        .withDockerImage(dockerImageName);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.CHECK_CONNECTION_SOURCE)
        .withCheckConnection(jobCheckConnectionConfig);

    return createPendingJob(scope, jobConfig);
  }

  @Override
  public long createDestinationCheckConnectionJob(DestinationConnection destination, String dockerImageName) throws IOException {
    final String scope =
        ScopeHelper.createScope(
            JobConfig.ConfigType.CHECK_CONNECTION_DESTINATION,
            destination.getDestinationId().toString());

    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(destination.getConfiguration())
        .withDockerImage(dockerImageName);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.CHECK_CONNECTION_DESTINATION)
        .withCheckConnection(jobCheckConnectionConfig);

    return createPendingJob(scope, jobConfig);
  }

  @Override
  public long createDiscoverSchemaJob(SourceConnection source, String dockerImageName) throws IOException {
    final String scope = ScopeHelper.createScope(
        JobConfig.ConfigType.DISCOVER_SCHEMA,
        source.getSourceId().toString());

    final JobDiscoverCatalogConfig jobDiscoverCatalogConfig = new JobDiscoverCatalogConfig()
        .withConnectionConfiguration(source.getConfiguration())
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
  public long createSyncJob(SourceConnection source,
                            DestinationConnection destination,
                            StandardSync standardSync,
                            String sourceDockerImageName,
                            String destinationDockerImageName)
      throws IOException {
    final UUID connectionId = standardSync.getConnectionId();

    final String scope = ScopeHelper.createScope(JobConfig.ConfigType.SYNC, connectionId.toString());

    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withSourceConnection(source)
        .withSourceDockerImage(sourceDockerImageName)
        .withDestinationConnection(destination)
        .withDestinationDockerImage(destinationDockerImageName)
        .withStandardSync(standardSync);

    // todo (cgardens) - this will not have the intended behavior if the last job failed. then the next
    // job will assume there is no state and re-sync everything! this is already wrong, so i'm not going
    // to increase the scope of the current project.
    final Optional<Job> previousJobOptional = getLastSyncJob(connectionId);

    final Optional<State> stateOptional = previousJobOptional.flatMap(j -> {
      final List<Attempt> attempts = j.getAttempts() != null ? j.getAttempts() : Lists.newArrayList();
      // find oldest attempt that is either succeeded or contains state.
      return attempts.stream()
          .filter(
              a -> a.getStatus() == AttemptStatus.COMPLETED || a.getOutput().map(JobOutput::getSync).map(StandardSyncOutput::getState).isPresent())
          .max(Comparator.comparingLong(Attempt::getCreatedAtInSecond))
          .map(Attempt::getOutput)
          .map(Optional::get)
          .map(JobOutput::getSync)
          .map(StandardSyncOutput::getState);
    });
    stateOptional.ifPresent(jobSyncConfig::withState);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.SYNC)
        .withSync(jobSyncConfig);
    return createPendingJob(scope, jobConfig);
  }

  // todo
  private Optional<State> getPreviousState() {
    return null;
  };

  // configJson is a oneOf checkConnection, discoverSchema, sync
  private long createPendingJob(String scope, JobConfig jobConfig) throws IOException {
    LOGGER.info("creating pending job for scope: " + scope);
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);

    try {
      final Record record = database.query(
          ctx -> ctx.fetch(
              "INSERT INTO jobs(scope, created_at, updated_at, status, config) VALUES(?, ?, ?, CAST(? AS JOB_STATUS), CAST(? as JSONB)) RETURNING id",
              scope,
              now,
              now,
              JobStatus.PENDING.toString().toLowerCase(),
              Jsons.serialize(jobConfig)))
          .stream()
          .findFirst()
          .orElseThrow(() -> new RuntimeException("This should not happen"));
      return record.getValue("id", Long.class);
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  // todo fix
  @Override
  public void updateStatus(long jobId, JobStatus status) throws IOException {
    LOGGER.info("Setting job status to " + status + " for job " + jobId);
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);

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
  public long createAttempt(long jobId, Path logPath) throws IOException {
    final Job job = getJob(jobId);
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);
    try {
      return database.query(
          ctx -> ctx.fetch(
              "INSERT INTO attempts(job_id, attempt_id, log_path, status, started_at, created_at, updated_at) VALUES(?, ?, ?, CAST(? AS ATTEMPT_STATUS), ?, ?, ?) RETURNING attempt_id",
              jobId,
              job.getNumAttempts(),
              logPath.toString(),
              AttemptStatus.RUNNING.toString().toLowerCase(),
              now,
              now,
              now))
          .stream()
          .findFirst()
          .map(r -> r.get("attempt_id", Long.class))
          .orElseThrow(() -> new RuntimeException("This should not happen"));
    } catch (SQLException e) {
      throw new IOException(e);
    }

  }

  @Override
  public <T> void writeOutput(long jobId, long attemptId, T output) throws IOException {
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);

    try {
      database.query(
          ctx -> ctx.execute(
              "UPDATE attempts SET output = CAST(? as JSONB), updated_at = ? WHERE attempt_id = ? AND job_id = ?",
              Jsons.serialize(output),
              now,
              attemptId,
              jobId));
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  @Override
  public Job getJob(long jobId) throws IOException {
    try {
      return database.query(
          ctx -> getJobFromResult(ctx.fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE jobs.id = ?", jobId))
              .orElseThrow(() -> new RuntimeException("Could not find job with id: " + jobId)));
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  @Override
  public List<Job> listJobs(JobConfig.ConfigType configType, String configId) throws IOException {
    try {
      final String scope = ScopeHelper.createScope(configType, configId);
      return database.query(ctx -> getJobsFromResult(ctx.fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE scope = ? ORDER BY jobs.created_at DESC", scope)));
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
      return database.query(ctx -> getJobsFromResult(ctx
          .fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE jobs.scope LIKE " + likeStatement
              + " AND CAST(jobs.status AS VARCHAR) = ? ORDER BY jobs.created_at DESC",
              status.toString().toLowerCase())));
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  @Override
  public Optional<Job> getLastSyncJob(UUID connectionId) throws IOException {
    try {
      return database.query(ctx -> getJobFromResult(ctx
          .fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE scope = ? AND CAST(jobs.status AS VARCHAR) <> ? ORDER BY jobs.created_at DESC LIMIT 1",
              ScopeHelper.createScope(JobConfig.ConfigType.SYNC, connectionId.toString()),
              JobStatus.CANCELLED.toString().toLowerCase())));
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  @Override
  public Optional<Job> getOldestPendingJob() throws IOException {
    try {
      return database.query(ctx -> getJobFromResult(ctx
          .fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE CAST(jobs.status AS VARCHAR) = 'pending' ORDER BY jobs.created_at ASC LIMIT 1")));
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  // record) interactions are confined to this class. would like to keep it that way for now, but
  // once we have other classes that interact with the db, this can be moved out.
  public static List<Job> getJobsFromResult(Result<Record> result) {
    final Map<Long, List<Record>> jobIdToAttempts = result.stream().collect(Collectors.groupingBy(r -> r.getValue("job_id", Long.class)));

    return jobIdToAttempts.values().stream()
        .map(records -> {
          final Record jobEntry = records.get(0);

          List<Attempt> attempts = Collections.emptyList();
          if (jobEntry.get("attempt_id") != null) {
            attempts = records.stream().map(attemptRecord -> {
              final String outputDb = jobEntry.get("attempt_output", String.class);
              final JobOutput output = outputDb == null ? null : Jsons.deserialize(outputDb, JobOutput.class);
              return new Attempt(
                  attemptRecord.get("attempt_id", Long.class),
                  attemptRecord.get("job_id", Long.class),
                  Path.of(jobEntry.get("log_path", String.class)),
                  output,
                  AttemptStatus.valueOf(jobEntry.get("attempt_status", String.class).toUpperCase()),
                  Optional.ofNullable(jobEntry.get("attempt_started_at")).map(value -> getEpoch(jobEntry, "attempt_started_at")).orElse(null),
                  getEpoch(jobEntry, "attempt_created_at"),
                  getEpoch(jobEntry, "attempt_updated_at"));
            })
                .collect(Collectors.toList());
          }
          final JobConfig jobConfig = Jsons.deserialize(jobEntry.get("config", String.class), JobConfig.class);
          return new Job(
              jobEntry.get("job_id", Long.class),
              jobEntry.get("scope", String.class),
              jobConfig,
              attempts,
              JobStatus.valueOf(jobEntry.get("job_status", String.class).toUpperCase()),
              Optional.ofNullable(jobEntry.get("job_started_at")).map(value -> getEpoch(jobEntry, "started_at")).orElse(null),
              getEpoch(jobEntry, "job_created_at"),
              getEpoch(jobEntry, "job_updated_at"));
        }).collect(Collectors.toList());
  }

  public static Optional<Job> getJobFromResult(Result<Record> result) {
    return getJobsFromResult(result).stream().findFirst();
  }

  private static long getEpoch(Record record, String fieldName) {
    return record.get(fieldName, LocalDateTime.class).toEpochSecond(ZoneOffset.UTC);
  }

}
