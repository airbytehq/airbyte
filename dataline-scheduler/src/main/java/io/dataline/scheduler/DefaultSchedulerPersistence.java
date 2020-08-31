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

import io.dataline.commons.json.Jsons;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.JobCheckConnectionConfig;
import io.dataline.config.JobConfig;
import io.dataline.config.JobDiscoverSchemaConfig;
import io.dataline.config.JobOutput;
import io.dataline.config.JobSyncConfig;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.StandardSyncOutput;
import io.dataline.db.DatabaseHelper;
import io.dataline.integrations.Integrations;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Record;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class DefaultSchedulerPersistence implements SchedulerPersistence {

  private static final Logger LOGGER = LoggerFactory.getLogger(DefaultSchedulerPersistence.class);
  private final BasicDataSource connectionPool;

  public DefaultSchedulerPersistence(BasicDataSource connectionPool) {
    this.connectionPool = connectionPool;
  }

  @Override
  public long createSourceCheckConnectionJob(SourceConnectionImplementation sourceImplementation)
      throws IOException {
    final String scope =
        ScopeHelper.createScope(
            JobConfig.ConfigType.CHECK_CONNECTION_SOURCE,
            sourceImplementation.getSourceImplementationId().toString());

    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig();
    jobCheckConnectionConfig.setConnectionConfigurationJson(
        sourceImplementation.getConfigurationJson());
    jobCheckConnectionConfig.setDockerImage(
        Integrations.findBySpecId(sourceImplementation.getSourceSpecificationId())
            .getCheckConnectionImage());

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setConfigType(JobConfig.ConfigType.CHECK_CONNECTION_SOURCE);
    jobConfig.setCheckConnection(jobCheckConnectionConfig);

    return createPendingJob(scope, jobConfig);
  }

  @Override
  public long createDestinationCheckConnectionJob(DestinationConnectionImplementation destinationImplementation)
      throws IOException {
    final String scope =
        ScopeHelper.createScope(
            JobConfig.ConfigType.CHECK_CONNECTION_DESTINATION,
            destinationImplementation.getDestinationImplementationId().toString());

    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig();
    jobCheckConnectionConfig.setConnectionConfigurationJson(
        destinationImplementation.getConfigurationJson());
    jobCheckConnectionConfig.setDockerImage(
        Integrations.findBySpecId(destinationImplementation.getDestinationSpecificationId())
            .getCheckConnectionImage());

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setConfigType(JobConfig.ConfigType.CHECK_CONNECTION_DESTINATION);
    jobConfig.setCheckConnection(jobCheckConnectionConfig);

    return createPendingJob(scope, jobConfig);
  }

  @Override
  public long createDiscoverSchemaJob(SourceConnectionImplementation sourceImplementation)
      throws IOException {

    final String scope =
        ScopeHelper.createScope(
            JobConfig.ConfigType.DISCOVER_SCHEMA,
            sourceImplementation.getSourceImplementationId().toString());

    final JobDiscoverSchemaConfig jobDiscoverSchemaConfig = new JobDiscoverSchemaConfig();
    jobDiscoverSchemaConfig.setConnectionConfigurationJson(
        sourceImplementation.getConfigurationJson());
    jobDiscoverSchemaConfig.setDockerImage(
        Integrations.findBySpecId(sourceImplementation.getSourceSpecificationId())
            .getDiscoverSchemaImage());

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setConfigType(JobConfig.ConfigType.DISCOVER_SCHEMA);
    jobConfig.setDiscoverSchema(jobDiscoverSchemaConfig);

    return createPendingJob(scope, jobConfig);
  }

  @Override
  public long createSyncJob(SourceConnectionImplementation sourceImplementation,
                            DestinationConnectionImplementation destinationImplementation,
                            StandardSync standardSync)
      throws IOException {
    final UUID connectionId = standardSync.getConnectionId();

    final String scope =
        ScopeHelper.createScope(JobConfig.ConfigType.SYNC, connectionId.toString());

    final JobSyncConfig jobSyncConfig = new JobSyncConfig();
    jobSyncConfig.setSourceConnectionImplementation(sourceImplementation);
    jobSyncConfig.setSourceDockerImage(
        Integrations.findBySpecId(sourceImplementation.getSourceSpecificationId()).getSyncImage());
    jobSyncConfig.setDestinationConnectionImplementation(destinationImplementation);
    jobSyncConfig.setDestinationDockerImage(
        Integrations.findBySpecId(destinationImplementation.getDestinationImplementationId())
            .getSyncImage());
    jobSyncConfig.setStandardSync(standardSync);

    final Optional<Job> previousJobOptional =
        JobUtils.getLastSyncJobForConnectionId(connectionPool, connectionId);
    final Optional<StandardSyncOutput> standardSyncOutput =
        previousJobOptional.flatMap(Job::getOutput).map(JobOutput::getSync);

    standardSyncOutput.map(StandardSyncOutput::getState).ifPresent(jobSyncConfig::setState);

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setConfigType(JobConfig.ConfigType.SYNC);
    jobConfig.setSync(jobSyncConfig);
    return createPendingJob(scope, jobConfig);
  }

  // configJson is a oneOf checkConnection, discoverSchema, sync
  public long createPendingJob(String scope, JobConfig jobConfig) throws IOException {
    LOGGER.info("creating pending job for scope: " + scope);
    LocalDateTime now = LocalDateTime.ofInstant(Instant.now(), ZoneOffset.UTC);

    final String configJson = Jsons.serialize(jobConfig);

    final Record record;
    try {
      record =
          DatabaseHelper.query(
              connectionPool,
              ctx -> ctx.fetch(
                  "INSERT INTO jobs(scope, created_at, updated_at, status, config, output, stdout_path, stderr_path) VALUES(?, ?, ?, CAST(? AS JOB_STATUS), CAST(? as JSONB), ?, ?, ?) RETURNING id",
                  scope,
                  now,
                  now,
                  JobStatus.PENDING.toString().toLowerCase(),
                  configJson,
                  null,
                  JobLogs.getLogDirectory(scope),
                  JobLogs.getLogDirectory(scope)))
              .stream()
              .findFirst()
              .orElseThrow(() -> new RuntimeException("This should not happen"));
    } catch (SQLException e) {
      LOGGER.error("sql", e);
      throw new IOException(e);
    }
    return record.getValue("id", Long.class);
  }

  @Override
  public Job getJob(long jobId) throws IOException {
    try {
      return DatabaseHelper.query(
          connectionPool,
          ctx -> {
            Record jobEntry =
                ctx.fetch("SELECT * FROM jobs WHERE id = ?", jobId).stream()
                    .findFirst()
                    .orElseThrow(
                        () -> new RuntimeException("Could not find job with id: " + jobId));

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
      return DatabaseHelper.query(
          connectionPool,
          ctx -> ctx.fetch("SELECT * FROM jobs WHERE scope = ?", scope).stream()
              .map(DefaultSchedulerPersistence::getJobFromRecord)
              .collect(Collectors.toList()));
    } catch (SQLException e) {
      throw new IOException(e);
    }
  }

  public static Job getJobFromRecord(Record jobEntry) {
    final JobConfig jobConfig =
        Jsons.deserialize(jobEntry.get("config", String.class), JobConfig.class);

    final String outputDb = jobEntry.get("output", String.class);
    final JobOutput output = outputDb == null ? null : Jsons.deserialize(outputDb, JobOutput.class);

    return new Job(
        jobEntry.get("id", Long.class),
        jobEntry.getValue("scope", String.class),
        JobStatus.valueOf(jobEntry.getValue("status", String.class).toUpperCase()),
        jobConfig,
        output,
        jobEntry.get("stdout_path", String.class),
        jobEntry.get("stderr_path", String.class),
        getEpoch(jobEntry, "created_at"),
        Optional.ofNullable(jobEntry.get("started_at"))
            .map(value -> getEpoch(jobEntry, "started_at"))
            .orElse(null),
        getEpoch(jobEntry, "updated_at"));
  }

  private static long getEpoch(Record record, String fieldName) {
    return record.getValue(fieldName, LocalDateTime.class).toEpochSecond(ZoneOffset.UTC);
  }

}
