/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence;

import static io.airbyte.db.instance.jobs.jooq.generated.Tables.ATTEMPTS;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.JsonNodeType;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.annotations.VisibleForTesting;
import com.google.common.collect.Iterators;
import com.google.common.collect.Sets;
import com.google.common.collect.UnmodifiableIterator;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.commons.text.Names;
import io.airbyte.commons.text.Sqls;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobOutput;
import io.airbyte.db.Database;
import io.airbyte.db.ExceptionWrappingDatabase;
import io.airbyte.db.instance.jobs.JobsDatabaseSchema;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.scheduler.models.Attempt;
import io.airbyte.scheduler.models.AttemptStatus;
import io.airbyte.scheduler.models.AttemptWithJobInfo;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import io.airbyte.scheduler.models.JobWithStatusAndTimestamp;
import java.io.IOException;
import java.math.BigInteger;
import java.nio.file.Path;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.OffsetDateTime;
import java.time.ZoneOffset;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;
import java.util.function.Supplier;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.InsertValuesStepN;
import org.jooq.JSONB;
import org.jooq.Named;
import org.jooq.Record;
import org.jooq.Result;
import org.jooq.Sequence;
import org.jooq.Table;
import org.jooq.impl.DSL;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultJobPersistence implements JobPersistence {

  // not static because job history test case manipulates these.
  private final int JOB_HISTORY_MINIMUM_AGE_IN_DAYS;
  private final int JOB_HISTORY_MINIMUM_RECENCY;
  private final int JOB_HISTORY_EXCESSIVE_NUMBER_OF_JOBS;

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultJobPersistence.class);
  private static final Set<String> SYSTEM_SCHEMA = Set
      .of("pg_toast", "information_schema", "pg_catalog", "import_backup", "pg_internal",
          "catalog_history");
  public static final String ATTEMPT_NUMBER = "attempt_number";
  private static final String JOB_ID = "job_id";
  private static final String WHERE = "WHERE ";
  private static final String AND = " AND ";
  private static final String SCOPE_CLAUSE = "scope = ? AND ";

  protected static final String DEFAULT_SCHEMA = "public";
  private static final String BACKUP_SCHEMA = "import_backup";
  public static final String DEPLOYMENT_ID_KEY = "deployment_id";
  public static final String METADATA_KEY_COL = "key";
  public static final String METADATA_VAL_COL = "value";

  @VisibleForTesting
  static final String BASE_JOB_SELECT_AND_JOIN = jobSelectAndJoin("jobs");

  private static final String AIRBYTE_METADATA_TABLE = "airbyte_metadata";
  public static final String ORDER_BY_JOB_TIME_ATTEMPT_TIME =
      "ORDER BY jobs.created_at DESC, jobs.id DESC, attempts.created_at ASC, attempts.id ASC ";

  private final ExceptionWrappingDatabase jobDatabase;
  private final Supplier<Instant> timeSupplier;

  @VisibleForTesting
  DefaultJobPersistence(final Database jobDatabase,
                        final Supplier<Instant> timeSupplier,
                        final int minimumAgeInDays,
                        final int excessiveNumberOfJobs,
                        final int minimumRecencyCount) {
    this.jobDatabase = new ExceptionWrappingDatabase(jobDatabase);
    this.timeSupplier = timeSupplier;
    JOB_HISTORY_MINIMUM_AGE_IN_DAYS = minimumAgeInDays;
    JOB_HISTORY_EXCESSIVE_NUMBER_OF_JOBS = excessiveNumberOfJobs;
    JOB_HISTORY_MINIMUM_RECENCY = minimumRecencyCount;
  }

  public DefaultJobPersistence(final Database jobDatabase) {
    this(jobDatabase, Instant::now, 30, 500, 10);
  }

  private static String jobSelectAndJoin(String jobsSubquery) {
    return "SELECT\n"
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
        + "attempts.failure_summary AS attempt_failure_summary,\n"
        + "attempts.created_at AS attempt_created_at,\n"
        + "attempts.updated_at AS attempt_updated_at,\n"
        + "attempts.ended_at AS attempt_ended_at\n"
        + "FROM " + jobsSubquery + " LEFT OUTER JOIN attempts ON jobs.id = attempts.job_id ";
  }

  /**
   * @param scope This is the primary id of a standard sync (StandardSync#connectionId).
   */
  @Override
  public Optional<Long> enqueueJob(final String scope, final JobConfig jobConfig) throws IOException {
    LOGGER.info("enqueuing pending job for scope: {}", scope);
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);

    final String queueingRequest = Job.REPLICATION_TYPES.contains(jobConfig.getConfigType())
        ? String.format("WHERE NOT EXISTS (SELECT 1 FROM jobs WHERE config_type IN (%s) AND scope = '%s' AND status NOT IN (%s)) ",
            Job.REPLICATION_TYPES.stream().map(Sqls::toSqlName).map(Names::singleQuote).collect(Collectors.joining(",")),
            scope,
            JobStatus.TERMINAL_STATUSES.stream().map(Sqls::toSqlName).map(Names::singleQuote).collect(Collectors.joining(",")))
        : "";

    return jobDatabase.query(
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
  public void resetJob(final long jobId) throws IOException {
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);
    jobDatabase.query(ctx -> {
      updateJobStatus(ctx, jobId, JobStatus.PENDING, now);
      return null;
    });
  }

  @Override
  public void cancelJob(final long jobId) throws IOException {
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);
    jobDatabase.query(ctx -> {
      updateJobStatus(ctx, jobId, JobStatus.CANCELLED, now);
      return null;
    });
  }

  @Override
  public void failJob(final long jobId) throws IOException {
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);
    jobDatabase.query(ctx -> {
      updateJobStatus(ctx, jobId, JobStatus.FAILED, now);
      return null;
    });
  }

  private void updateJobStatus(final DSLContext ctx, final long jobId, final JobStatus newStatus, final LocalDateTime now) {
    final Job job = getJob(ctx, jobId);
    job.validateStatusTransition(newStatus);
    ctx.execute(
        "UPDATE jobs SET status = CAST(? as JOB_STATUS), updated_at = ? WHERE id = ?",
        Sqls.toSqlName(newStatus),
        now,
        jobId);
  }

  @Override
  public int createAttempt(final long jobId, final Path logPath) throws IOException {
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);

    return jobDatabase.transaction(ctx -> {
      final Job job = getJob(ctx, jobId);
      if (job.isJobInTerminalState()) {
        final var errMsg = String.format(
            "Cannot create an attempt for a job id: %s that is in a terminal state: %s for connection id: %s",
            job.getId(), job.getStatus(), job.getScope());
        throw new IllegalStateException(errMsg);
      }

      if (job.hasRunningAttempt()) {
        final var errMsg = String.format(
            "Cannot create an attempt for a job id: %s that has a running attempt: %s for connection id: %s",
            job.getId(), job.getStatus(), job.getScope());
        throw new IllegalStateException(errMsg);
      }

      updateJobStatus(ctx, jobId, JobStatus.RUNNING, now);

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
          .map(r -> r.get(ATTEMPT_NUMBER, Integer.class))
          .orElseThrow(() -> new RuntimeException("This should not happen"));
    });

  }

  @Override
  public void failAttempt(final long jobId, final int attemptNumber) throws IOException {
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);
    jobDatabase.transaction(ctx -> {
      updateJobStatus(ctx, jobId, JobStatus.INCOMPLETE, now);

      ctx.execute(
          "UPDATE attempts SET status = CAST(? as ATTEMPT_STATUS), updated_at = ? , ended_at = ? WHERE job_id = ? AND attempt_number = ?",
          Sqls.toSqlName(AttemptStatus.FAILED),
          now,
          now,
          jobId,
          attemptNumber);
      return null;
    });
  }

  @Override
  public void succeedAttempt(final long jobId, final int attemptNumber) throws IOException {
    final LocalDateTime now = LocalDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);
    jobDatabase.transaction(ctx -> {
      updateJobStatus(ctx, jobId, JobStatus.SUCCEEDED, now);

      ctx.execute(
          "UPDATE attempts SET status = CAST(? as ATTEMPT_STATUS), updated_at = ? , ended_at = ? WHERE job_id = ? AND attempt_number = ?",
          Sqls.toSqlName(AttemptStatus.SUCCEEDED),
          now,
          now,
          jobId,
          attemptNumber);
      return null;
    });
  }

  @Override
  public void setAttemptTemporalWorkflowId(final long jobId, final int attemptNumber, final String temporalWorkflowId) throws IOException {
    jobDatabase.query(ctx -> ctx.execute(
        " UPDATE attempts SET temporal_workflow_id = ? WHERE job_id = ? AND attempt_number = ?",
        temporalWorkflowId,
        jobId,
        attemptNumber));
  }

  @Override
  public Optional<String> getAttemptTemporalWorkflowId(final long jobId, final int attemptNumber) throws IOException {
    final var result = jobDatabase.query(ctx -> ctx.fetch(
        " SELECT temporal_workflow_id from attempts WHERE job_id = ? AND attempt_number = ?",
        jobId,
        attemptNumber)).stream().findFirst();

    if (result.isEmpty() || result.get().get("temporal_workflow_id") == null) {
      return Optional.empty();
    }

    return Optional.of(result.get().get("temporal_workflow_id", String.class));
  }

  @Override
  public <T> void writeOutput(final long jobId, final int attemptNumber, final T output) throws IOException {
    final OffsetDateTime now = OffsetDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);
    jobDatabase.transaction(
        ctx -> ctx.update(ATTEMPTS)
            .set(ATTEMPTS.OUTPUT, JSONB.valueOf(Jsons.serialize(output)))
            .set(ATTEMPTS.UPDATED_AT, now)
            .where(ATTEMPTS.JOB_ID.eq(jobId), ATTEMPTS.ATTEMPT_NUMBER.eq(attemptNumber))
            .execute());
  }

  @Override
  public void writeAttemptFailureSummary(final long jobId, final int attemptNumber, final AttemptFailureSummary failureSummary) throws IOException {
    final OffsetDateTime now = OffsetDateTime.ofInstant(timeSupplier.get(), ZoneOffset.UTC);

    jobDatabase.transaction(
        ctx -> ctx.update(ATTEMPTS)
            .set(ATTEMPTS.FAILURE_SUMMARY, JSONB.valueOf(Jsons.serialize(failureSummary)))
            .set(ATTEMPTS.UPDATED_AT, now)
            .where(ATTEMPTS.JOB_ID.eq(jobId), ATTEMPTS.ATTEMPT_NUMBER.eq(attemptNumber))
            .execute());
  }

  @Override
  public Job getJob(final long jobId) throws IOException {
    return jobDatabase.query(ctx -> getJob(ctx, jobId));
  }

  private Job getJob(final DSLContext ctx, final long jobId) {
    return getJobOptional(ctx, jobId).orElseThrow(() -> new RuntimeException("Could not find job with id: " + jobId));
  }

  private Optional<Job> getJobOptional(final DSLContext ctx, final long jobId) {
    return getJobFromResult(ctx.fetch(BASE_JOB_SELECT_AND_JOIN + "WHERE jobs.id = ?", jobId));
  }

  @Override
  public List<Job> listJobs(final ConfigType configType, final String configId, final int pagesize, final int offset) throws IOException {
    return listJobs(Set.of(configType), configId, pagesize, offset);
  }

  @Override
  public List<Job> listJobs(final Set<ConfigType> configTypes, final String configId, final int pagesize, final int offset) throws IOException {
    final String jobsSubquery = "(SELECT * FROM jobs WHERE CAST(jobs.config_type AS VARCHAR) in " + Sqls.toSqlInFragment(configTypes)
        + " AND jobs.scope = '" + configId + "' ORDER BY jobs.created_at DESC, jobs.id DESC LIMIT " + pagesize + " OFFSET " + offset + ") AS jobs";
    return jobDatabase.query(ctx -> getJobsFromResult(ctx.fetch(
        jobSelectAndJoin(jobsSubquery) + ORDER_BY_JOB_TIME_ATTEMPT_TIME)));
  }

  @Override
  public List<Job> listJobsWithStatus(final JobStatus status) throws IOException {
    return listJobsWithStatus(Sets.newHashSet(ConfigType.values()), status);
  }

  @Override
  public List<Job> listJobsWithStatus(final Set<ConfigType> configTypes, final JobStatus status) throws IOException {
    return jobDatabase.query(ctx -> getJobsFromResult(ctx
        .fetch(BASE_JOB_SELECT_AND_JOIN + WHERE +
            "CAST(config_type AS VARCHAR) IN " + Sqls.toSqlInFragment(configTypes) + AND +
            "CAST(jobs.status AS VARCHAR) = ? " +
            ORDER_BY_JOB_TIME_ATTEMPT_TIME,
            Sqls.toSqlName(status))));
  }

  @Override
  public List<Job> listJobsWithStatus(final ConfigType configType, final JobStatus status) throws IOException {
    return listJobsWithStatus(Sets.newHashSet(configType), status);
  }

  @Override
  public List<Job> listJobsForConnectionWithStatuses(final UUID connectionId, final Set<ConfigType> configTypes, final Set<JobStatus> statuses)
      throws IOException {
    return jobDatabase.query(ctx -> getJobsFromResult(ctx
        .fetch(BASE_JOB_SELECT_AND_JOIN + WHERE +
            SCOPE_CLAUSE +
            "config_type IN " + Sqls.toSqlInFragment(configTypes) + AND +
            "jobs.status IN " + Sqls.toSqlInFragment(statuses) + " " +
            ORDER_BY_JOB_TIME_ATTEMPT_TIME,
            connectionId.toString())));
  }

  @Override
  public List<JobWithStatusAndTimestamp> listJobStatusAndTimestampWithConnection(final UUID connectionId,
                                                                                 final Set<ConfigType> configTypes,
                                                                                 final Instant jobCreatedAtTimestamp)
      throws IOException {
    final LocalDateTime timeConvertedIntoLocalDateTime = LocalDateTime.ofInstant(jobCreatedAtTimestamp, ZoneOffset.UTC);

    final String JobStatusSelect = "SELECT id, status, created_at, updated_at FROM jobs ";
    return jobDatabase.query(ctx -> ctx
        .fetch(JobStatusSelect + WHERE +
            SCOPE_CLAUSE +
            "CAST(config_type AS VARCHAR) in " + Sqls.toSqlInFragment(configTypes) + AND +
            "created_at >= ? ORDER BY created_at DESC", connectionId.toString(), timeConvertedIntoLocalDateTime))
        .stream()
        .map(r -> new JobWithStatusAndTimestamp(
            r.get("id", Long.class),
            JobStatus.valueOf(r.get("status", String.class).toUpperCase()),
            r.get("created_at", Long.class) / 1000,
            r.get("updated_at", Long.class) / 1000))
        .toList();
  }

  @Override
  public Optional<Job> getLastReplicationJob(final UUID connectionId) throws IOException {
    return jobDatabase.query(ctx -> ctx
        .fetch(BASE_JOB_SELECT_AND_JOIN + WHERE +
            "CAST(jobs.config_type AS VARCHAR) in " + Sqls.toSqlInFragment(Job.REPLICATION_TYPES) + AND +
            SCOPE_CLAUSE +
            "CAST(jobs.status AS VARCHAR) <> ? " +
            "ORDER BY jobs.created_at DESC LIMIT 1",
            connectionId.toString(),
            Sqls.toSqlName(JobStatus.CANCELLED))
        .stream()
        .findFirst()
        .flatMap(r -> getJobOptional(ctx, r.get(JOB_ID, Long.class))));
  }

  @Override
  public Optional<Job> getFirstReplicationJob(final UUID connectionId) throws IOException {
    return jobDatabase.query(ctx -> ctx
        .fetch(BASE_JOB_SELECT_AND_JOIN + WHERE +
            "CAST(jobs.config_type AS VARCHAR) in " + Sqls.toSqlInFragment(Job.REPLICATION_TYPES) + AND +
            SCOPE_CLAUSE +
            "CAST(jobs.status AS VARCHAR) <> ? " +
            "ORDER BY jobs.created_at ASC LIMIT 1",
            connectionId.toString(),
            Sqls.toSqlName(JobStatus.CANCELLED))
        .stream()
        .findFirst()
        .flatMap(r -> getJobOptional(ctx, r.get(JOB_ID, Long.class))));
  }

  @Override
  public Optional<Job> getNextJob() throws IOException {
    // rules:
    // 1. get oldest, pending job
    // 2. job is excluded if another job of the same scope is already running
    // 3. job is excluded if another job of the same scope is already incomplete
    return jobDatabase.query(ctx -> ctx
        .fetch(BASE_JOB_SELECT_AND_JOIN + WHERE +
            "CAST(jobs.status AS VARCHAR) = 'pending' AND " +
            "jobs.scope NOT IN ( SELECT scope FROM jobs WHERE status = 'running' OR status = 'incomplete' ) " +
            "ORDER BY jobs.created_at ASC LIMIT 1")
        .stream()
        .findFirst()
        .flatMap(r -> getJobOptional(ctx, r.get(JOB_ID, Long.class))));
  }

  @Override
  public List<Job> listJobs(final ConfigType configType, final Instant attemptEndedAtTimestamp) throws IOException {
    final LocalDateTime timeConvertedIntoLocalDateTime = LocalDateTime.ofInstant(attemptEndedAtTimestamp, ZoneOffset.UTC);
    return jobDatabase.query(ctx -> getJobsFromResult(ctx
        .fetch(BASE_JOB_SELECT_AND_JOIN + WHERE +
            "CAST(config_type AS VARCHAR) =  ? AND " +
            " attempts.ended_at > ? ORDER BY jobs.created_at ASC, attempts.created_at ASC", Sqls.toSqlName(configType),
            timeConvertedIntoLocalDateTime)));
  }

  @Override
  public List<AttemptWithJobInfo> listAttemptsWithJobInfo(final ConfigType configType, final Instant attemptEndedAtTimestamp) throws IOException {
    final LocalDateTime timeConvertedIntoLocalDateTime = LocalDateTime.ofInstant(attemptEndedAtTimestamp, ZoneOffset.UTC);
    return jobDatabase.query(ctx -> getAttemptsWithJobsFromResult(ctx.fetch(
        BASE_JOB_SELECT_AND_JOIN + WHERE + "CAST(config_type AS VARCHAR) =  ? AND " + " attempts.ended_at > ? ORDER BY attempts.ended_at ASC",
        Sqls.toSqlName(configType),
        timeConvertedIntoLocalDateTime)));
  }

  // Retrieves only Job information from the record, without any attempt info
  private static Job getJobFromRecord(final Record record) {
    return new Job(record.get(JOB_ID, Long.class),
        Enums.toEnum(record.get("config_type", String.class), ConfigType.class).orElseThrow(),
        record.get("scope", String.class),
        Jsons.deserialize(record.get("config", String.class), JobConfig.class),
        new ArrayList<Attempt>(),
        JobStatus.valueOf(record.get("job_status", String.class).toUpperCase()),
        Optional.ofNullable(record.get("job_started_at")).map(value -> getEpoch(record, "started_at")).orElse(null),
        getEpoch(record, "job_created_at"),
        getEpoch(record, "job_updated_at"));
  }

  private static Attempt getAttemptFromRecord(final Record record) {
    return new Attempt(
        record.get(ATTEMPT_NUMBER, Long.class),
        record.get(JOB_ID, Long.class),
        Path.of(record.get("log_path", String.class)),
        record.get("attempt_output", String.class) == null ? null : Jsons.deserialize(record.get("attempt_output", String.class), JobOutput.class),
        Enums.toEnum(record.get("attempt_status", String.class), AttemptStatus.class).orElseThrow(),
        record.get("attempt_failure_summary", String.class) == null ? null
            : Jsons.deserialize(record.get("attempt_failure_summary", String.class), AttemptFailureSummary.class),
        getEpoch(record, "attempt_created_at"),
        getEpoch(record, "attempt_updated_at"),
        Optional.ofNullable(record.get("attempt_ended_at"))
            .map(value -> getEpoch(record, "attempt_ended_at"))
            .orElse(null));
  }

  private static List<AttemptWithJobInfo> getAttemptsWithJobsFromResult(final Result<Record> result) {
    return result
        .stream()
        .filter(record -> record.getValue(ATTEMPT_NUMBER) != null)
        .map(record -> new AttemptWithJobInfo(getAttemptFromRecord(record), getJobFromRecord(record)))
        .collect(Collectors.toList());
  }

  private static List<Job> getJobsFromResult(final Result<Record> result) {
    // keeps results strictly in order so the sql query controls the sort
    final List<Job> jobs = new ArrayList<Job>();
    Job currentJob = null;
    for (final Record entry : result) {
      if (currentJob == null || currentJob.getId() != entry.get(JOB_ID, Long.class)) {
        currentJob = getJobFromRecord(entry);
        jobs.add(currentJob);
      }
      if (entry.getValue(ATTEMPT_NUMBER) != null) {
        currentJob.getAttempts().add(getAttemptFromRecord(entry));
      }
    }

    return jobs;
  }

  @VisibleForTesting
  static Optional<Job> getJobFromResult(final Result<Record> result) {
    return getJobsFromResult(result).stream().findFirst();
  }

  private static long getEpoch(final Record record, final String fieldName) {
    return record.get(fieldName, LocalDateTime.class).toEpochSecond(ZoneOffset.UTC);
  }

  private final String SECRET_MIGRATION_STATUS = "secretMigration";

  @Override
  public boolean isSecretMigrated() throws IOException {
    final Result<Record> result = jobDatabase.query(ctx -> ctx.select()
        .from(AIRBYTE_METADATA_TABLE)
        .where(DSL.field(METADATA_KEY_COL).eq(SECRET_MIGRATION_STATUS))
        .fetch());

    return result.stream().count() == 1;
  }

  @Override
  public void setSecretMigrationDone() throws IOException {
    jobDatabase.query(ctx -> ctx.execute(String.format(
        "INSERT INTO %s(%s, %s) VALUES('%s', '%s') ON CONFLICT (%s) DO UPDATE SET %s = '%s'",
        AIRBYTE_METADATA_TABLE,
        METADATA_KEY_COL,
        METADATA_VAL_COL,
        SECRET_MIGRATION_STATUS,
        true,
        METADATA_KEY_COL,
        METADATA_VAL_COL,
        true)));
  }

  private final String SCHEDULER_MIGRATION_STATUS = "schedulerMigration";

  @Override
  public boolean isSchedulerMigrated() throws IOException {
    final Result<Record> result = jobDatabase.query(ctx -> ctx.select()
        .from(AIRBYTE_METADATA_TABLE)
        .where(DSL.field(METADATA_KEY_COL).eq(SCHEDULER_MIGRATION_STATUS))
        .fetch());

    return result.stream().count() == 1;
  }

  @Override
  public void setSchedulerMigrationDone() throws IOException {
    jobDatabase.query(ctx -> ctx.execute(String.format(
        "INSERT INTO %s(%s, %s) VALUES('%s', '%s') ON CONFLICT (%s) DO UPDATE SET %s = '%s'",
        AIRBYTE_METADATA_TABLE,
        METADATA_KEY_COL,
        METADATA_VAL_COL,
        SCHEDULER_MIGRATION_STATUS,
        true,
        METADATA_KEY_COL,
        METADATA_VAL_COL,
        true)));
  }

  @Override
  public Optional<String> getVersion() throws IOException {
    final Result<Record> result = jobDatabase.query(ctx -> ctx.select()
        .from(AIRBYTE_METADATA_TABLE)
        .where(DSL.field(METADATA_KEY_COL).eq(AirbyteVersion.AIRBYTE_VERSION_KEY_NAME))
        .fetch());
    return result.stream().findFirst().map(r -> r.getValue(METADATA_VAL_COL, String.class));
  }

  @Override
  public void setVersion(final String airbyteVersion) throws IOException {
    jobDatabase.query(ctx -> ctx.execute(String.format(
        "INSERT INTO %s(%s, %s) VALUES('%s', '%s'), ('%s_init_db', '%s') ON CONFLICT (%s) DO UPDATE SET %s = '%s'",
        AIRBYTE_METADATA_TABLE,
        METADATA_KEY_COL,
        METADATA_VAL_COL,
        AirbyteVersion.AIRBYTE_VERSION_KEY_NAME,
        airbyteVersion,
        current_timestamp(),
        airbyteVersion,
        METADATA_KEY_COL,
        METADATA_VAL_COL,
        airbyteVersion)));
  }

  @Override
  public Optional<UUID> getDeployment() throws IOException {
    final Result<Record> result = jobDatabase.query(ctx -> ctx.select()
        .from(AIRBYTE_METADATA_TABLE)
        .where(DSL.field(METADATA_KEY_COL).eq(DEPLOYMENT_ID_KEY))
        .fetch());
    return result.stream().findFirst().map(r -> UUID.fromString(r.getValue(METADATA_VAL_COL, String.class)));
  }

  @Override
  public void setDeployment(final UUID deployment) throws IOException {
    // if an existing deployment id already exists, on conflict, return it so we can log it.
    final UUID committedDeploymentId = jobDatabase.query(ctx -> ctx.fetch(String.format(
        "INSERT INTO %s(%s, %s) VALUES('%s', '%s') ON CONFLICT (%s) DO NOTHING RETURNING (SELECT %s FROM %s WHERE %s='%s') as existing_deployment_id",
        AIRBYTE_METADATA_TABLE,
        METADATA_KEY_COL,
        METADATA_VAL_COL,
        DEPLOYMENT_ID_KEY,
        deployment,
        METADATA_KEY_COL,
        METADATA_VAL_COL,
        AIRBYTE_METADATA_TABLE,
        METADATA_KEY_COL,
        DEPLOYMENT_ID_KEY)))
        .stream()
        .filter(record -> record.get("existing_deployment_id", String.class) != null)
        .map(record -> UUID.fromString(record.get("existing_deployment_id", String.class)))
        .findFirst()
        .orElse(deployment); // if no record was returned that means that the new deployment id was used.

    if (!deployment.equals(committedDeploymentId)) {
      LOGGER.warn("Attempted to set a deployment id %s, but deployment id %s already set. Retained original value.");
    }
  }

  private static String current_timestamp() {
    return ZonedDateTime.now().format(DateTimeFormatter.ISO_OFFSET_DATE_TIME);
  }

  @Override
  public Map<JobsDatabaseSchema, Stream<JsonNode>> exportDatabase() throws IOException {
    return exportDatabase(DEFAULT_SCHEMA);
  }

  /**
   * This is different from {@link #exportDatabase()} cause it exports all the tables in all the
   * schemas available
   */
  @Override
  public Map<String, Stream<JsonNode>> dump() throws IOException {
    final Map<String, Stream<JsonNode>> result = new HashMap<>();
    for (final String schema : listSchemas()) {
      final List<String> tables = listAllTables(schema);

      for (final String table : tables) {
        if (result.containsKey(table)) {
          throw new RuntimeException("Multiple tables found with the same name " + table);
        }
        result.put(table.toUpperCase(), exportTable(schema, table));
      }
    }

    return result;
  }

  private Map<JobsDatabaseSchema, Stream<JsonNode>> exportDatabase(final String schema) throws IOException {
    final List<String> tables = listTables(schema);
    final Map<JobsDatabaseSchema, Stream<JsonNode>> result = new HashMap<>();

    for (final String table : tables) {
      result.put(JobsDatabaseSchema.valueOf(table.toUpperCase()), exportTable(schema, table));
    }

    return result;
  }

  /**
   * List tables from @param schema and @return their names
   */
  private List<String> listTables(final String schema) throws IOException {
    if (schema != null) {
      return jobDatabase.query(context -> context.meta().getSchemas(schema).stream()
          .flatMap(s -> context.meta(s).getTables().stream())
          .map(Named::getName)
          .filter(table -> JobsDatabaseSchema.getTableNames().contains(table.toLowerCase()))
          .collect(Collectors.toList()));
    } else {
      return List.of();
    }
  }

  @Override
  public void purgeJobHistory() {
    purgeJobHistory(LocalDateTime.now());
  }

  @VisibleForTesting
  public void purgeJobHistory(final LocalDateTime asOfDate) {
    try {
      final String JOB_HISTORY_PURGE_SQL = MoreResources.readResource("job_history_purge.sql");
      // interval '?' days cannot use a ? bind, so we're using %d instead.
      final String sql = String.format(JOB_HISTORY_PURGE_SQL, (JOB_HISTORY_MINIMUM_AGE_IN_DAYS - 1));
      jobDatabase.query(ctx -> ctx.execute(sql,
          asOfDate.format(DateTimeFormatter.ofPattern("YYYY-MM-dd")),
          JOB_HISTORY_EXCESSIVE_NUMBER_OF_JOBS,
          JOB_HISTORY_MINIMUM_RECENCY));
    } catch (final IOException e) {
      throw new RuntimeException(e);
    }
  }

  private List<String> listAllTables(final String schema) throws IOException {
    if (schema != null) {
      return jobDatabase.query(context -> context.meta().getSchemas(schema).stream()
          .flatMap(s -> context.meta(s).getTables().stream())
          .map(Named::getName)
          .collect(Collectors.toList()));
    } else {
      return List.of();
    }
  }

  private List<String> listSchemas() throws IOException {
    return jobDatabase.query(context -> context.meta().getSchemas().stream()
        .map(Named::getName)
        .filter(c -> !SYSTEM_SCHEMA.contains(c))
        .collect(Collectors.toList()));

  }

  private Stream<JsonNode> exportTable(final String schema, final String tableName) throws IOException {
    final Table<Record> tableSql = getTable(schema, tableName);
    try (final Stream<Record> records = jobDatabase.query(ctx -> ctx.select(DSL.asterisk()).from(tableSql).fetchStream())) {
      return records.map(record -> {
        final Set<String> jsonFieldNames = Arrays.stream(record.fields())
            .filter(f -> "jsonb".equals(f.getDataType().getTypeName()))
            .map(Field::getName)
            .collect(Collectors.toSet());
        final JsonNode row = Jsons.deserialize(record.formatJSON(JdbcUtils.getDefaultJSONFormat()));
        // for json fields, deserialize them so they are treated as objects instead of strings. this is to
        // get around that formatJson doesn't handle deserializing them for us.
        jsonFieldNames.forEach(jsonFieldName -> ((ObjectNode) row).replace(jsonFieldName, Jsons.deserialize(row.get(jsonFieldName).asText())));
        return row;
      });
    }
  }

  @Override
  public void importDatabase(final String airbyteVersion, final Map<JobsDatabaseSchema, Stream<JsonNode>> data) throws IOException {
    importDatabase(airbyteVersion, DEFAULT_SCHEMA, data, false);
  }

  private void importDatabase(final String airbyteVersion,
                              final String targetSchema,
                              final Map<JobsDatabaseSchema, Stream<JsonNode>> data,
                              final boolean incrementalImport)
      throws IOException {
    if (!data.isEmpty()) {
      createSchema(BACKUP_SCHEMA);
      jobDatabase.transaction(ctx -> {
        // obtain locks on all tables first, to prevent deadlocks
        for (final JobsDatabaseSchema tableType : data.keySet()) {
          ctx.execute(String.format("LOCK TABLE %s IN ACCESS EXCLUSIVE MODE", tableType.name()));
        }
        for (final JobsDatabaseSchema tableType : data.keySet()) {
          if (!incrementalImport) {
            truncateTable(ctx, targetSchema, tableType.name(), BACKUP_SCHEMA);
          }
          importTable(ctx, targetSchema, tableType, data.get(tableType));
        }
        registerImportMetadata(ctx, airbyteVersion);
        return null;
      });
    }
    // TODO write "import success vXX on now()" to audit log table?
  }

  private void createSchema(final String schema) throws IOException {
    jobDatabase.query(ctx -> ctx.createSchemaIfNotExists(schema).execute());
  }

  /**
   * In a single transaction, truncate all @param tables from @param schema, making backup copies
   * in @param backupSchema
   */
  private static void truncateTable(final DSLContext ctx, final String schema, final String tableName, final String backupSchema) {
    final Table<Record> tableSql = getTable(schema, tableName);
    final Table<Record> backupTableSql = getTable(backupSchema, tableName);
    ctx.dropTableIfExists(backupTableSql).execute();
    ctx.createTable(backupTableSql).as(DSL.select(DSL.asterisk()).from(tableSql)).withData().execute();
    ctx.truncateTable(tableSql).restartIdentity().execute();
  }

  /**
   * TODO: we need version specific importers to copy data to the database. Issue: #5682.
   */
  private static void importTable(final DSLContext ctx, final String schema, final JobsDatabaseSchema tableType, final Stream<JsonNode> jsonStream) {
    LOGGER.info("Importing table {} from archive into database.", tableType.name());
    final Table<Record> tableSql = getTable(schema, tableType.name());
    final JsonNode jsonSchema = tableType.getTableDefinition();
    if (jsonSchema != null) {
      // Use an ArrayList to mirror the order of columns from the schema file since columns may not be
      // written consistently in the same order in the stream
      final List<Field<?>> columns = getFields(jsonSchema);
      // Build a Stream of List of Values using the same order as columns, filling blanks if needed (when
      // stream omits them for nullable columns)
      final Stream<List<?>> data = jsonStream.map(node -> {
        final List<Object> values = new ArrayList<>();
        for (final Field<?> column : columns) {
          values.add(getJsonNodeValue(node, column.getName()));
        }
        return values;
      });
      // Then insert rows into table in batches, to avoid crashing due to inserting too much data at once
      final UnmodifiableIterator<List<List<?>>> partitions = Iterators.partition(data.iterator(), 100);
      partitions.forEachRemaining(values -> {
        final InsertValuesStepN<Record> insertStep = ctx
            .insertInto(tableSql)
            .columns(columns);

        values.forEach(insertStep::values);

        if (insertStep.getBindValues().size() > 0) {
          // LOGGER.debug(insertStep.toString());
          ctx.batch(insertStep).execute();
        }
      });
      final Optional<Field<?>> idColumn = columns.stream().filter(f -> "id".equals(f.getName())).findFirst();
      if (idColumn.isPresent())
        resetIdentityColumn(ctx, schema, tableType);
    }
  }

  /**
   * In schema.sql, we create tables with IDENTITY PRIMARY KEY columns named 'id' that will generate
   * auto-incremented ID for each new record. When importing batch of records from outside of the DB,
   * we need to update Postgres Internal state to continue auto-incrementing from the latest value or
   * we would risk to violate primary key constraints by inserting new records with duplicate ids.
   *
   * This function reset such Identity states (called SQL Sequence objects).
   */
  private static void resetIdentityColumn(final DSLContext ctx, final String schema, final JobsDatabaseSchema tableType) {
    final Result<Record> result = ctx.fetch(String.format("SELECT MAX(id) FROM %s.%s", schema, tableType.name()));
    final Optional<Integer> maxId = result.stream()
        .map(r -> r.get(0, Integer.class))
        .filter(Objects::nonNull)
        .findFirst();
    if (maxId.isPresent()) {
      final Sequence<BigInteger> sequenceName = DSL.sequence(DSL.name(schema, String.format("%s_%s_seq", tableType.name().toLowerCase(), "id")));
      ctx.alterSequenceIfExists(sequenceName).restartWith(maxId.get() + 1).execute();
    }
  }

  /**
   * Insert records into the metadata table to keep track of import Events that were applied on the
   * database. Update and overwrite the corresponding @param airbyteVersion.
   */
  private static void registerImportMetadata(final DSLContext ctx, final String airbyteVersion) {
    ctx.execute(String.format("INSERT INTO %s VALUES('%s_import_db', '%s');", AIRBYTE_METADATA_TABLE, current_timestamp(), airbyteVersion));
    ctx.execute(String.format("UPDATE %s SET %s = '%s' WHERE %s = '%s';",
        AIRBYTE_METADATA_TABLE,
        METADATA_VAL_COL,
        airbyteVersion,
        METADATA_KEY_COL,
        AirbyteVersion.AIRBYTE_VERSION_KEY_NAME));
  }

  /**
   * Read @param jsonSchema and @returns a list of properties (converted as Field objects)
   */
  @SuppressWarnings("PMD.ForLoopCanBeForeach")
  private static List<Field<?>> getFields(final JsonNode jsonSchema) {
    final List<Field<?>> result = new ArrayList<>();
    final JsonNode properties = jsonSchema.get("properties");
    for (final Iterator<String> it = properties.fieldNames(); it.hasNext();) {
      final String fieldName = it.next();
      result.add(DSL.field(fieldName));
    }
    return result;
  }

  /**
   * @return Java Values for the @param columnName in @param jsonNode
   */
  private static Object getJsonNodeValue(final JsonNode jsonNode, final String columnName) {
    if (!jsonNode.has(columnName)) {
      return null;
    }
    final JsonNode valueNode = jsonNode.get(columnName);
    final JsonNodeType nodeType = valueNode.getNodeType();
    if (nodeType == JsonNodeType.OBJECT) {
      return valueNode.toString();
    } else if (nodeType == JsonNodeType.STRING) {
      return valueNode.asText();
    } else if (nodeType == JsonNodeType.NUMBER) {
      return valueNode.asDouble();
    } else if (nodeType == JsonNodeType.NULL) {
      return null;
    }
    throw new IllegalArgumentException(String.format("Undefined type for column %s", columnName));
  }

  private static Table<Record> getTable(final String schema, final String tableName) {
    return DSL.table(String.format("%s.%s", schema, tableName));
  }

}
