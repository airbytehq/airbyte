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
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobOutput;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.scheduler.Attempt;
import io.airbyte.scheduler.AttemptStatus;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import io.airbyte.scheduler.ScopeHelper;
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
  public long enqueueJob(String scope, JobConfig jobConfig) throws IOException {
    LOGGER.info("enqueuing pending job for scope: " + scope);
    return internalCreateJob(scope, jobConfig, true).orElseThrow(() -> new RuntimeException("This should not happen"));
  }

  @Override
  public Optional<Long> enqueueSingletonJob(String scope, JobConfig jobConfig) throws IOException {
    LOGGER.info("attempt creating pending job for scope: " + scope);
    return internalCreateJob(scope, jobConfig, false);
  }

  private Optional<Long> internalCreateJob(String scope, JobConfig jobConfig, boolean allowQueueing) throws IOException {
    LOGGER.info("creating pending job for scope: " + scope);
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);

    String queueingRequest = !allowQueueing ? String.format("WHERE NOT EXISTS (SELECT 1 FROM jobs WHERE scope = '%s' and status NOT IN (%s)) ",
        scope,
        String.join(", ", getSQLTerminalStates())) : "";

    return database.query(
        ctx -> ctx.fetch(
            "INSERT INTO jobs(scope, created_at, updated_at, status, config) " +
                "SELECT ?, ?, ?, CAST(? AS JOB_STATUS), CAST(? as JSONB) " +
                queueingRequest +
                "RETURNING id ",
            scope,
            now,
            now,
            JobStatus.PENDING.toString().toLowerCase(),
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
          new IllegalStateException(String.format("Attempt to reset a job that is in a terminate state. job id: %s", jobId)));
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
        newStatus.toString().toLowerCase(),
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
          AttemptStatus.RUNNING.toString().toLowerCase(),
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
          AttemptStatus.FAILED.toString().toLowerCase(),
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
          AttemptStatus.SUCCEEDED.toString().toLowerCase(),
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
    return getJobFromResult(ctx.fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE jobs.id = ?", jobId))
        .orElseThrow(() -> new RuntimeException("Could not find job with id: " + jobId));
  }

  @Override
  public List<Job> listJobs(JobConfig.ConfigType configType, String configId) throws IOException {
    final String scope = ScopeHelper.createScope(configType, configId);
    return database.query(ctx -> getJobsFromResult(ctx.fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE scope = ? ORDER BY jobs.created_at DESC", scope)));
  }

  @Override
  public List<Job> listJobsWithStatus(JobConfig.ConfigType configType, JobStatus status) throws IOException {
    // todo (cgardens) - jooq does not let you use bindings to do LIKE queries. you have to construct
    // the string yourself or use their DSL.
    final String likeStatement = "'" + ScopeHelper.getScopePrefix(configType) + "%'";
    return database.query(ctx -> getJobsFromResult(ctx
        .fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE jobs.scope LIKE " + likeStatement
            + " AND CAST(jobs.status AS VARCHAR) = ? ORDER BY jobs.created_at DESC",
            status.toString().toLowerCase())));
  }

  @Override
  public Optional<Job> getLastSyncJob(UUID connectionId) throws IOException {
    return database.query(ctx -> getJobFromResult(ctx
        .fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE scope = ? AND CAST(jobs.status AS VARCHAR) <> ? ORDER BY jobs.created_at DESC LIMIT 1",
            ScopeHelper.createScope(JobConfig.ConfigType.SYNC, connectionId.toString()),
            JobStatus.CANCELLED.toString().toLowerCase())));
  }

  @Override
  public Optional<Job> getLastResetJob(UUID connectionId) throws IOException {
    return database.query(ctx -> getJobFromResult(ctx
        .fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE scope = ? AND CAST(jobs.status AS VARCHAR) <> ? ORDER BY jobs.created_at DESC LIMIT 1",
            ScopeHelper.createScope(JobConfig.ConfigType.RESET_CONNECTION, connectionId.toString()),
            JobStatus.CANCELLED.toString().toLowerCase())));
  }

  @Override
  public Optional<State> getCurrentState(UUID connectionId) throws IOException {
    return database.query(ctx -> getJobFromResult(ctx
        .fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE scope = ? AND CAST(jobs.status AS VARCHAR) = ? ORDER BY attempts.created_at DESC LIMIT 1",
            ScopeHelper.createScope(JobConfig.ConfigType.SYNC, connectionId.toString()),
            JobStatus.SUCCEEDED.toString().toLowerCase())))
        .flatMap(Job::getSuccessOutput)
        .map(JobOutput::getSync)
        .map(StandardSyncOutput::getState);
  }

  @Override
  public Optional<Job> getNextJob() throws IOException {
    // rules:
    // 1. get oldest, pending job
    // 2. job is excluded if another job of the same scope is already running
    // 3. job is excluded if another job of the same scope is already incomplete
    return database.query(ctx -> getJobFromResult(ctx
        .fetch(BASE_JOB_SELECT_AND_JOIN
            + "WHERE CAST(jobs.status AS VARCHAR) = 'pending' AND jobs.scope NOT IN ( SELECT scope FROM jobs WHERE status = 'running' OR status = 'incomplete' ) ORDER BY jobs.created_at ASC LIMIT 1")));
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
                  AttemptStatus.valueOf(attemptRecord.get("attempt_status", String.class).toUpperCase()),
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

  private static List<String> getSQLTerminalStates() {
    return JobStatus.TERMINAL_STATUSES.stream()
        .map(JobStatus::toString)
        .map(String::toLowerCase)
        .map(s -> String.format("'%s'", s))
        .collect(Collectors.toList());
  }

}
