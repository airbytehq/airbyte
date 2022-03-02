/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.converters;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.google.common.collect.Lists;
import io.airbyte.api.model.AttemptFailureOrigin;
import io.airbyte.api.model.AttemptFailureReason;
import io.airbyte.api.model.AttemptFailureSummary;
import io.airbyte.api.model.AttemptFailureType;
import io.airbyte.api.model.AttemptInfoRead;
import io.airbyte.api.model.AttemptRead;
import io.airbyte.api.model.AttemptStats;
import io.airbyte.api.model.AttemptStreamStats;
import io.airbyte.api.model.DestinationDefinitionRead;
import io.airbyte.api.model.JobConfigType;
import io.airbyte.api.model.JobDebugRead;
import io.airbyte.api.model.JobInfoRead;
import io.airbyte.api.model.JobRead;
import io.airbyte.api.model.JobWithAttemptsRead;
import io.airbyte.api.model.LogRead;
import io.airbyte.api.model.SourceDefinitionRead;
import io.airbyte.commons.enums.Enums;
import io.airbyte.commons.version.AirbyteVersion;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.FailureReason.FailureType;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobOutput.OutputType;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StreamSyncStats;
import io.airbyte.config.SyncStats;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.scheduler.models.Attempt;
import io.airbyte.scheduler.models.AttemptStatus;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.models.JobStatus;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JobConverterTest {

  private static final long JOB_ID = 100L;
  private static final long ATTEMPT_ID = 1002L;
  private static final String JOB_CONFIG_ID = "123";
  private static final JobStatus JOB_STATUS = JobStatus.RUNNING;
  private static final AttemptStatus ATTEMPT_STATUS = AttemptStatus.RUNNING;
  private static final JobConfig.ConfigType CONFIG_TYPE = JobConfig.ConfigType.CHECK_CONNECTION_SOURCE;
  private static final JobConfig JOB_CONFIG = new JobConfig()
      .withConfigType(CONFIG_TYPE)
      .withCheckConnection(new JobCheckConnectionConfig());
  private static final Path LOG_PATH = Path.of("log_path");
  private static final long CREATED_AT = System.currentTimeMillis() / 1000;
  private static final long RECORDS_EMITTED = 15L;
  private static final long BYTES_EMITTED = 100L;
  private static final long RECORDS_COMMITTED = 10L;
  private static final long STATE_MESSAGES_EMITTED = 2L;
  private static final String STREAM_NAME = "stream1";
  private static final String FAILURE_EXTERNAL_MESSAGE = "something went wrong";
  private static final long FAILURE_TIMESTAMP = System.currentTimeMillis();
  private static final String FAILURE_STACKTRACE = "stacktrace";
  private static final boolean PARTIAL_SUCCESS = false;

  private static final JobOutput JOB_OUTPUT = new JobOutput()
      .withOutputType(OutputType.SYNC)
      .withSync(new StandardSyncOutput()
          .withStandardSyncSummary(new StandardSyncSummary()
              .withRecordsSynced(RECORDS_EMITTED)
              .withBytesSynced(BYTES_EMITTED)
              .withTotalStats(new SyncStats()
                  .withRecordsEmitted(RECORDS_EMITTED)
                  .withBytesEmitted(BYTES_EMITTED)
                  .withStateMessagesEmitted(STATE_MESSAGES_EMITTED)
                  .withRecordsCommitted(RECORDS_COMMITTED))
              .withStreamStats(Lists.newArrayList(new StreamSyncStats()
                  .withStreamName(STREAM_NAME)
                  .withStats(new SyncStats()
                      .withRecordsEmitted(RECORDS_EMITTED)
                      .withBytesEmitted(BYTES_EMITTED)
                      .withStateMessagesEmitted(STATE_MESSAGES_EMITTED)
                      .withRecordsCommitted(RECORDS_COMMITTED))))));

  private JobConverter jobConverter;
  private Job job;

  private static final JobInfoRead JOB_INFO =
      new JobInfoRead()
          .job(new JobRead()
              .id(JOB_ID)
              .configId(JOB_CONFIG_ID)
              .status(io.airbyte.api.model.JobStatus.RUNNING)
              .configType(JobConfigType.CHECK_CONNECTION_SOURCE)
              .createdAt(CREATED_AT)
              .updatedAt(CREATED_AT))
          .attempts(Lists.newArrayList(new AttemptInfoRead()
              .attempt(new AttemptRead()
                  .id(ATTEMPT_ID)
                  .status(io.airbyte.api.model.AttemptStatus.RUNNING)
                  .recordsSynced(RECORDS_EMITTED)
                  .bytesSynced(BYTES_EMITTED)
                  .totalStats(new AttemptStats()
                      .recordsEmitted(RECORDS_EMITTED)
                      .bytesEmitted(BYTES_EMITTED)
                      .stateMessagesEmitted(STATE_MESSAGES_EMITTED)
                      .recordsCommitted(RECORDS_COMMITTED))
                  .streamStats(Lists.newArrayList(new AttemptStreamStats()
                      .streamName(STREAM_NAME)
                      .stats(new AttemptStats()
                          .recordsEmitted(RECORDS_EMITTED)
                          .bytesEmitted(BYTES_EMITTED)
                          .stateMessagesEmitted(STATE_MESSAGES_EMITTED)
                          .recordsCommitted(RECORDS_COMMITTED))))
                  .updatedAt(CREATED_AT)
                  .createdAt(CREATED_AT)
                  .endedAt(CREATED_AT)
                  .failureSummary(new AttemptFailureSummary()
                      .failures(Lists.newArrayList(new AttemptFailureReason()
                          .failureOrigin(AttemptFailureOrigin.SOURCE)
                          .failureType(AttemptFailureType.SYSTEM_ERROR)
                          .externalMessage(FAILURE_EXTERNAL_MESSAGE)
                          .stacktrace(FAILURE_STACKTRACE)
                          .timestamp(FAILURE_TIMESTAMP)))
                      .partialSuccess(PARTIAL_SUCCESS)))
              .logs(new LogRead().logLines(new ArrayList<>()))));

  private static final String version = "0.33.4";
  private static final AirbyteVersion airbyteVersion = new AirbyteVersion(version);
  private static final SourceDefinitionRead sourceDefinitionRead = new SourceDefinitionRead().sourceDefinitionId(UUID.randomUUID());
  private static final DestinationDefinitionRead destinationDefinitionRead =
      new DestinationDefinitionRead().destinationDefinitionId(UUID.randomUUID());

  private static final JobDebugRead JOB_DEBUG_INFO =
      new JobDebugRead()
          .id(JOB_ID)
          .configId(JOB_CONFIG_ID)
          .status(io.airbyte.api.model.JobStatus.RUNNING)
          .configType(JobConfigType.CHECK_CONNECTION_SOURCE)
          .airbyteVersion(airbyteVersion.serialize())
          .sourceDefinition(sourceDefinitionRead)
          .destinationDefinition(destinationDefinitionRead);

  private static final JobWithAttemptsRead JOB_WITH_ATTEMPTS_READ = new JobWithAttemptsRead()
      .job(JOB_INFO.getJob())
      .attempts(JOB_INFO.getAttempts().stream().map(AttemptInfoRead::getAttempt).collect(Collectors.toList()));

  private static final io.airbyte.config.AttemptFailureSummary FAILURE_SUMMARY = new io.airbyte.config.AttemptFailureSummary()
      .withFailures(Lists.newArrayList(new FailureReason()
          .withFailureOrigin(FailureOrigin.SOURCE)
          .withFailureType(FailureType.SYSTEM_ERROR)
          .withExternalMessage(FAILURE_EXTERNAL_MESSAGE)
          .withStacktrace(FAILURE_STACKTRACE)
          .withTimestamp(FAILURE_TIMESTAMP)))
      .withPartialSuccess(PARTIAL_SUCCESS);

  @BeforeEach
  public void setUp() {
    jobConverter = new JobConverter(WorkerEnvironment.DOCKER, LogConfigs.EMPTY);
    job = mock(Job.class);
    final Attempt attempt = mock(Attempt.class);
    when(job.getId()).thenReturn(JOB_ID);
    when(job.getConfigType()).thenReturn(JOB_CONFIG.getConfigType());
    when(job.getScope()).thenReturn(JOB_CONFIG_ID);
    when(job.getConfig()).thenReturn(JOB_CONFIG);
    when(job.getStatus()).thenReturn(JOB_STATUS);
    when(job.getCreatedAtInSecond()).thenReturn(CREATED_AT);
    when(job.getUpdatedAtInSecond()).thenReturn(CREATED_AT);
    when(job.getAttempts()).thenReturn(Lists.newArrayList(attempt));
    when(attempt.getId()).thenReturn(ATTEMPT_ID);
    when(attempt.getStatus()).thenReturn(ATTEMPT_STATUS);
    when(attempt.getOutput()).thenReturn(Optional.of(JOB_OUTPUT));
    when(attempt.getLogPath()).thenReturn(LOG_PATH);
    when(attempt.getCreatedAtInSecond()).thenReturn(CREATED_AT);
    when(attempt.getUpdatedAtInSecond()).thenReturn(CREATED_AT);
    when(attempt.getEndedAtInSecond()).thenReturn(Optional.of(CREATED_AT));
    when(attempt.getFailureSummary()).thenReturn(Optional.of(FAILURE_SUMMARY));

  }

  @Test
  public void testGetJobInfoRead() {
    assertEquals(JOB_INFO, jobConverter.getJobInfoRead(job));
  }

  @Test
  public void testGetDebugJobInfoRead() {
    assertEquals(JOB_DEBUG_INFO, jobConverter.getDebugJobInfoRead(JOB_INFO, sourceDefinitionRead, destinationDefinitionRead, airbyteVersion));
  }

  @Test
  public void testGetJobWithAttemptsRead() {
    assertEquals(JOB_WITH_ATTEMPTS_READ, jobConverter.getJobWithAttemptsRead(job));
  }

  @Test
  public void testGetJobRead() {
    final JobWithAttemptsRead jobReadActual = jobConverter.getJobWithAttemptsRead(job);
    assertEquals(JOB_WITH_ATTEMPTS_READ, jobReadActual);
  }

  @Test
  public void testEnumConversion() {
    assertTrue(Enums.isCompatible(JobConfig.ConfigType.class, JobConfigType.class));
    assertTrue(Enums.isCompatible(JobStatus.class, io.airbyte.api.model.JobStatus.class));
    assertTrue(Enums.isCompatible(AttemptStatus.class, io.airbyte.api.model.AttemptStatus.class));
  }

}
