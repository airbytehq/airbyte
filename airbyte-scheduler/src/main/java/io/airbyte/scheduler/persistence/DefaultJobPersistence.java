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
import com.google.common.collect.Sets;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.text.Names;
import io.airbyte.commons.text.Sqls;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.scheduler.Attempt;
import io.airbyte.scheduler.AttemptStatus;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import org.jooq.DSLContext;
import org.jooq.Record;
import org.jooq.Result;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultJobPersistence implements JobPersistence {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultJobPersistence.class);
  @VisibleForTesting
  static final String BASE_JOB_SELECT_AND_JOIN =
      "SELECT\n"
          + "jobs.id AS job_id,\n"
          + "jobs.config_type AS config_type,\n"
          + "jobs.scope AS scope,\n"
          + "jobs.config AS config,\n"
          + "jobs.status AS job_status,\n"
          + "jobs.started_at AS job_started_at,\n"
          + "jobs.created_at AS job_created_at,\n"
          + "jobs.updated_at AS job_updated_at,\n"
          + "attempts.attempt_number AS attempt_number,\n"
          + "attempts.log_path AS log_path,\n"
          + "attempts.output AS attempt_output,\n"
          + "attempts.status AS attempt_status,\n"
          + "attempts.created_at AS attempt_created_at,\n"
          + "attempts.updated_at AS attempt_updated_at,\n"
          + "attempts.ended_at AS attempt_ended_at\n"
          + "FROM jobs LEFT OUTER JOIN attempts ON jobs.id = attempts.job_id ";

  private final ExceptionWrappingDatabase database;
  private final Supplier<Instant> timeSupplier;

  @VisibleForTesting
  DefaultJobPersistence(Database database, Supplier<Instant> timeSupplier) {
    this.database = new ExceptionWrappingDatabase(database);
    this.timeSupplier = timeSupplier;
  }

  public DefaultJobPersistence(Database database) {
    this(database, Instant::now);
  }

  @Override
  public Optional<Long> enqueueJob(String scope, JobConfig jobConfig) throws IOException {
    LOGGER.info("enqueuing pending job for scope: {}", scope);
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);

    String queueingRequest = Job.REPLICATION_TYPES.contains(jobConfig.getConfigType())
        ? String.format("WHERE NOT EXISTS (SELECT 1 FROM jobs WHERE config_type IN (%s) AND scope = '%s' AND status NOT IN (%s)) ",
            Job.REPLICATION_TYPES.stream().map(Sqls::toSqlName).map(Names::singleQuote).collect(Collectors.joining(",")),
            scope,
            JobStatus.TERMINAL_STATUSES.stream().map(Sqls::toSqlName).map(Names::singleQuote).collect(Collectors.joining(",")))
        : "";

    return database.query(
        ctx -> ctx.fetch(
            "INSERT INTO jobs(config_type, scope, created_at, updated_at, status, config) " +
                "SELECT CAST(? AS JOB_CONFIG_TYPE), ?, ?, ?, CAST(? AS JOB_STATUS), CAST(? as JSONB) " +
                queueingRequest +
                "RETURNING id ",
            Sqls.toSqlName(jobConfig.getConfigType()),
            scope,
            now,
            now,
            Sqls.toSqlName(JobStatus.PENDING),
            Jsons.serialize(jobConfig)))
        .stream()
        .findFirst()
        .map(r -> r.getValue("id", Long.class));
  }

  @Override
  public void resetJob(long jobId) throws IOException {
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);
    database.query(ctx -> {
      updateJobStatusIfNotInTerminalState(ctx, jobId, JobStatus.PENDING, now,
          new IllegalStateException(String.format("Attempt to reset a job that is in a terminal state. job id: %s", jobId)));
      return null;
    });
  }

  @Override
  public void cancelJob(long jobId) throws IOException {
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);
    database.query(ctx -> {
      updateJobStatusIfNotInTerminalState(ctx, jobId, JobStatus.CANCELLED, now);
      return null;
    });
  }

  @Override
  public void failJob(long jobId) throws IOException {
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);
    database.query(ctx -> {
      updateJobStatusIfNotInTerminalState(ctx, jobId, JobStatus.FAILED, now);
      return null;
    });
  }

  private void updateJobStatusIfNotInTerminalState(DSLContext ctx, long jobId, JobStatus newStatus, LocalDateTime now, RuntimeException e) {
    final Job job = getJob(ctx, jobId);
    if (!job.isJobInTerminalState()) {
      updateJobStatus(ctx, jobId, newStatus, now);
    } else if (e != null) {
      throw e;
    }
  }

  private void updateJobStatusIfNotInTerminalState(DSLContext ctx, long jobId, JobStatus newStatus, LocalDateTime now) {
    updateJobStatusIfNotInTerminalState(ctx, jobId, newStatus, now, null);
  }

  private void updateJobStatus(DSLContext ctx, long jobId, JobStatus newStatus, LocalDateTime now) {
    ctx.execute(
        "UPDATE jobs SET status = CAST(? as JOB_STATUS), updated_at = ? WHERE id = ?",
        Sqls.toSqlName(newStatus),
        now,
        jobId);
  }

  @Override
  public int createAttempt(long jobId, Path logPath) throws IOException {
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);

    return database.transaction(ctx -> {
      final Job job = getJob(ctx, jobId);
      if (job.isJobInTerminalState()) {
        throw new IllegalStateException("Cannot create an attempt for a job that is in a terminal state: " + job.getStatus());
      }

      if (job.hasRunningAttempt()) {
        throw new IllegalStateException("Cannot create an attempt for a job that has a running attempt: " + job.getStatus());
      }

      updateJobStatusIfNotInTerminalState(ctx, jobId, JobStatus.RUNNING, now);

      // will fail if attempt number already exists for the job id.
      return ctx.fetch(
          "INSERT INTO attempts(job_id, attempt_number, log_path, status, created_at, updated_at) VALUES(?, ?, ?, CAST(? AS ATTEMPT_STATUS), ?, ?) RETURNING attempt_number",
          jobId,
          job.getAttemptsCount(),
          logPath.toString(),
          Sqls.toSqlName(AttemptStatus.RUNNING),
          now,
          now)
          .stream()
          .findFirst()
          .map(r -> r.get("attempt_number", Integer.class))
          .orElseThrow(() -> new RuntimeException("This should not happen"));
    });

  }

  @Override
  public void failAttempt(long jobId, int attemptNumber) throws IOException {
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);
    database.transaction(ctx -> {
      // do not overwrite terminal states.
      updateJobStatusIfNotInTerminalState(ctx, jobId, JobStatus.INCOMPLETE, now);

      ctx.execute(
          "UPDATE attempts SET status = CAST(? as ATTEMPT_STATUS), updated_at = ? WHERE job_id = ? AND attempt_number = ?",
          Sqls.toSqlName(AttemptStatus.FAILED),
          now,
          jobId,
          attemptNumber);
      return null;
    });
  }

  @Override
  public void succeedAttempt(long jobId, int attemptNumber) throws IOException {
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);
    database.transaction(ctx -> {
      // override any other terminal statuses if we are now succeeded.
      updateJobStatus(ctx, jobId, JobStatus.SUCCEEDED, now);

      ctx.execute(
          "UPDATE attempts SET status = CAST(? as ATTEMPT_STATUS), updated_at = ? WHERE job_id = ? AND attempt_number = ?",
          Sqls.toSqlName(AttemptStatus.SUCCEEDED),
          now,
          jobId,
          attemptNumber);
      return null;
    });
  }

  @Override
  public <T> void writeOutput(long jobId, int attemptNumber, T output) throws IOException {
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);

    database.query(
        ctx -> ctx.execute(
            "UPDATE attempts SET output = CAST(? as JSONB), updated_at = ? WHERE job_id = ? AND attempt_number = ?",
            Jsons.serialize(output),
            now,
            jobId,
            attemptNumber));
  }

  @Override
  public Job getJob(long jobId) throws IOException {
    return database.query(ctx -> getJob(ctx, jobId));
  }

  private Job getJob(DSLContext ctx, long jobId) {
    return getJobOptional(ctx, jobId).orElseThrow(() -> new RuntimeException("Could not find job with id: " + jobId));
  }

  private Optional<Job> getJobOptional(DSLContext ctx, long jobId) {
    return getJobFromResult(ctx.fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE jobs.id = ?", jobId));
  }

  @Override
  public List<Job> listJobs(ConfigType configType, String configId) throws IOException {
    return database.query(ctx -> getJobsFromResult(ctx.fetch(
        BASE_JOB_SELECT_AND_JOIN + "WHERE " +
            "CAST(config_type AS VARCHAR) = ? AND " +
            "scope = ? " +
            "ORDER BY jobs.created_at DESC",
        Sqls.toSqlName(configType),
        configId)));
  }

  @Override
  public List<Job> listJobsWithStatus(JobStatus status) throws IOException {
    return listJobsWithStatus(Sets.newHashSet(ConfigType.values()), status);
  }

  @Override
  public List<Job> listJobsWithStatus(Set<ConfigType> configTypes, JobStatus status) throws IOException {
    return database.query(ctx -> getJobsFromResult(ctx
        .fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE " +
            "CAST(config_type AS VARCHAR) IN " + Sqls.toSqlInFragment(configTypes) + " AND " +
            "CAST(jobs.status AS VARCHAR) = ? " +
            "ORDER BY jobs.created_at DESC",
            Sqls.toSqlName(status))));
  }

  @Override
  public List<Job> listJobsWithStatus(ConfigType configType, JobStatus status) throws IOException {
    return listJobsWithStatus(Sets.newHashSet(configType), status);
  }

  @Override
  public Optional<Job> getLastReplicationJob(UUID connectionId) throws IOException {
    return database.query(ctx -> ctx
        .fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE " +
            "CAST(jobs.config_type AS VARCHAR) in " + Sqls.toSqlInFragment(Job.REPLICATION_TYPES) + " AND " +
            "scope = ? AND " +
            "CAST(jobs.status AS VARCHAR) <> ? " +
            "ORDER BY jobs.created_at DESC LIMIT 1",
            connectionId.toString(),
            Sqls.toSqlName(JobStatus.CANCELLED))
        .stream()
        .findFirst()
        .flatMap(r -> getJobOptional(ctx, r.get("job_id", Long.class))));
  }

  @Override
  public Optional<State> getCurrentState(UUID connectionId) throws IOException {
    return database.query(ctx -> ctx
        .fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE " +
            "CAST(jobs.config_type AS VARCHAR) in " + Sqls.toSqlInFragment(Job.REPLICATION_TYPES) + " AND " +
            "scope = ? AND " +
            "CAST(jobs.status AS VARCHAR) = ? " +
            "ORDER BY jobs.created_at DESC LIMIT 1",
            connectionId.toString(),
            Sqls.toSqlName(JobStatus.SUCCEEDED))
        .stream()
        .findFirst()
        .flatMap(r -> getJobOptional(ctx, r.get("job_id", Long.class)))
        .flatMap(Job::getSuccessOutput)
        .map(JobOutput::getSync)
        .map(StandardSyncOutput::getState));
  }

  @Override
  public Optional<Job> getNextJob() throws IOException {
    // rules:
    // 1. get oldest, pending job
    // 2. job is excluded if another job of the same scope is already running
    // 3. job is excluded if another job of the same scope is already incomplete
    return database.query(ctx -> ctx
        .fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE " +
            "CAST(jobs.status AS VARCHAR) = 'pending' AND " +
            "jobs.scope NOT IN ( SELECT scope FROM jobs WHERE status = 'running' OR status = 'incomplete' ) " +
            "ORDER BY jobs.created_at ASC LIMIT 1")
        .stream()
        .findFirst()
        .flatMap(r -> getJobOptional(ctx, r.get("job_id", Long.class))));
  }

  private static List<Job> getJobsFromResult(Result<Record> result) {
    final Map<Long, List<Record>> jobIdToAttempts = result.stream().collect(Collectors.groupingBy(r -> r.getValue("job_id", Long.class)));

    return jobIdToAttempts.values().stream()
        .map(records -> {
          final Record jobEntry = records.get(0);

          List<Attempt> attempts = Collections.emptyList();
          if (jobEntry.get("attempt_number") != null) {
            attempts = records.stream().map(attemptRecord -> {
              final String outputDb = attemptRecord.get("attempt_output", String.class);
              final JobOutput output = outputDb == null ? null : Jsons.deserialize(outputDb, JobOutput.class);
              return new Attempt(
                  attemptRecord.get("attempt_number", Long.class),
                  attemptRecord.get("job_id", Long.class),
                  Path.of(attemptRecord.get("log_path", String.class)),
                  output,
                  Enums.toEnum(attemptRecord.get("attempt_status", String.class), AttemptStatus.class).orElseThrow(),
                  getEpoch(attemptRecord, "attempt_created_at"),
                  getEpoch(attemptRecord, "attempt_updated_at"),
                  Optional.ofNullable(attemptRecord.get("attempt_ended_at"))
                      .map(value -> getEpoch(attemptRecord, "attempt_ended_at"))
                      .orElse(null));
            })
                .sorted(Comparator.comparingLong(Attempt::getId))
                .collect(Collectors.toList());
          }
          final JobConfig jobConfig = Jsons.deserialize(jobEntry.get("config", String.class), JobConfig.class);
          return new Job(
              jobEntry.get("job_id", Long.class),
              Enums.toEnum(jobEntry.get("config_type", String.class), ConfigType.class).orElseThrow(),
              jobEntry.get("scope", String.class),
              jobConfig,
              attempts,
              JobStatus.valueOf(jobEntry.get("job_status", String.class).toUpperCase()),
              Optional.ofNullable(jobEntry.get("job_started_at")).map(value -> getEpoch(jobEntry, "started_at")).orElse(null),
              getEpoch(jobEntry, "job_created_at"),
              getEpoch(jobEntry, "job_updated_at"));
        })
        .sorted(Comparator.comparingLong(Job::getCreatedAtInSecond).reversed())
        .collect(Collectors.toList());
  }

  public static Optional<Job> getJobFromResult(Result<Record> result) {
    return getJobsFromResult(result).stream().findFirst();
  }

  private static long getEpoch(Record record, String fieldName) {
    return record.get(fieldName, LocalDateTime.class).toEpochSecond(ZoneOffset.UTC);
  }

}
