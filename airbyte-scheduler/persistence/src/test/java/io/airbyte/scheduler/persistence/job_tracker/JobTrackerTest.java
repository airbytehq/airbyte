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

package io.airbyte.scheduler.persistence.job_tracker;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.Schedule;
import io.airbyte.config.Schedule.TimeUnit;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.scheduler.models.Attempt;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker.JobState;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.function.BiConsumer;
import java.util.function.Consumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class JobTrackerTest {

  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final UUID JOB_ID = UUID.randomUUID();
  private static final UUID UUID1 = UUID.randomUUID();
  private static final UUID UUID2 = UUID.randomUUID();
  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final String SOURCE_DEF_NAME = "postgres";
  private static final String DESTINATION_DEF_NAME = "bigquery";
  public static final String CONNECTOR_VERSION = "test";
  private static final long SYNC_START_TIME = 1000L;
  private static final long SYNC_END_TIME = 10000L;
  private static final long SYNC_DURATION = 9L; // in sync between end and start time
  private static final long SYNC_BYTES_SYNC = 42L;
  private static final long SYNC_RECORDS_SYNC = 4L;

  private static final ImmutableMap<String, Object> STARTED_STATE_METADATA = ImmutableMap.<String, Object>builder()
      .put("attempt_stage", "STARTED")
      .build();
  private static final ImmutableMap<String, Object> SUCCEEDED_STATE_METADATA = ImmutableMap.<String, Object>builder()
      .put("attempt_stage", "ENDED")
      .put("attempt_completion_status", JobState.SUCCEEDED)
      .build();
  private static final ImmutableMap<String, Object> FAILED_STATE_METADATA = ImmutableMap.<String, Object>builder()
      .put("attempt_stage", "ENDED")
      .put("attempt_completion_status", JobState.FAILED)
      .build();
  private static final ImmutableMap<String, Object> ATTEMPT_METADATA = ImmutableMap.<String, Object>builder()
      .put("duration", SYNC_DURATION)
      .put("volume_rows", SYNC_RECORDS_SYNC)
      .put("volume_mb", SYNC_BYTES_SYNC)
      .build();
  private static final ImmutableMap<String, Object> SYNC_CONFIG_METADATA = ImmutableMap.<String, Object>builder()
      .put(JobTracker.CONFIG + ".source.key", JobTracker.SET)
      .put(JobTracker.CONFIG + ".destination.key", false)
      .put(JobTracker.CATALOG + ".sync_mode.full_refresh", JobTracker.SET)
      .put(JobTracker.CATALOG + ".destination_sync_mode.append", JobTracker.SET)
      .put("namespace_definition", NamespaceDefinitionType.SOURCE)
      .put("table_prefix", false)
      .put("operation_count", 0)
      .build();

  private ConfigRepository configRepository;

  private JobPersistence jobPersistence;
  private TrackingClient trackingClient;
  private WorkspaceHelper workspaceHelper;
  private JobTracker jobTracker;

  @BeforeEach
  void setup() {
    configRepository = mock(ConfigRepository.class);
    jobPersistence = mock(JobPersistence.class);
    workspaceHelper = mock(WorkspaceHelper.class);
    trackingClient = mock(TrackingClient.class);
    jobTracker = new JobTracker(configRepository, jobPersistence, workspaceHelper, trackingClient);
  }

  @Test
  void testTrackCheckConnectionSource() throws ConfigNotFoundException, IOException, JsonValidationException {
    final ImmutableMap<String, Object> metadata = ImmutableMap.<String, Object>builder()
        .put("job_type", ConfigType.CHECK_CONNECTION_SOURCE)
        .put("job_id", JOB_ID.toString())
        .put("attempt_id", 0)
        .put("connector_source", SOURCE_DEF_NAME)
        .put("connector_source_definition_id", UUID1)
        .put("connector_source_version", CONNECTOR_VERSION)
        .build();

    when(configRepository.getStandardSourceDefinition(UUID1))
        .thenReturn(new StandardSourceDefinition()
            .withSourceDefinitionId(UUID1)
            .withName(SOURCE_DEF_NAME)
            .withDockerImageTag(CONNECTOR_VERSION));

    assertCheckConnCorrectMessageForEachState(
        (jobState, output) -> jobTracker.trackCheckConnectionSource(JOB_ID, UUID1, WORKSPACE_ID, jobState, output),
        metadata,
        true);
    assertCheckConnCorrectMessageForEachState(
        (jobState, output) -> jobTracker.trackCheckConnectionSource(JOB_ID, UUID1, null, jobState, output),
        metadata,
        false);
  }

  @Test
  void testTrackCheckConnectionDestination() throws ConfigNotFoundException, IOException, JsonValidationException {
    final ImmutableMap<String, Object> metadata = ImmutableMap.<String, Object>builder()
        .put("job_type", ConfigType.CHECK_CONNECTION_DESTINATION)
        .put("job_id", JOB_ID.toString())
        .put("attempt_id", 0)
        .put("connector_destination", DESTINATION_DEF_NAME)
        .put("connector_destination_definition_id", UUID2)
        .put("connector_destination_version", CONNECTOR_VERSION)
        .build();

    when(configRepository.getStandardDestinationDefinition(UUID2))
        .thenReturn(new StandardDestinationDefinition()
            .withDestinationDefinitionId(UUID2)
            .withName(DESTINATION_DEF_NAME)
            .withDockerImageTag(CONNECTOR_VERSION));

    assertCheckConnCorrectMessageForEachState(
        (jobState, output) -> jobTracker.trackCheckConnectionDestination(JOB_ID, UUID2, WORKSPACE_ID, jobState, output),
        metadata,
        true);
    assertCheckConnCorrectMessageForEachState(
        (jobState, output) -> jobTracker.trackCheckConnectionDestination(JOB_ID, UUID2, null, jobState, output),
        metadata,
        false);
  }

  @Test
  void testTrackDiscover() throws ConfigNotFoundException, IOException, JsonValidationException {
    final ImmutableMap<String, Object> metadata = ImmutableMap.<String, Object>builder()
        .put("job_type", ConfigType.DISCOVER_SCHEMA)
        .put("job_id", JOB_ID.toString())
        .put("attempt_id", 0)
        .put("connector_source", SOURCE_DEF_NAME)
        .put("connector_source_definition_id", UUID1)
        .put("connector_source_version", CONNECTOR_VERSION)
        .build();

    when(configRepository.getStandardSourceDefinition(UUID1))
        .thenReturn(new StandardSourceDefinition()
            .withSourceDefinitionId(UUID1)
            .withName(SOURCE_DEF_NAME)
            .withDockerImageTag(CONNECTOR_VERSION));

    assertCorrectMessageForEachState((jobState) -> jobTracker.trackDiscover(JOB_ID, UUID1, WORKSPACE_ID, jobState), metadata);
    assertCorrectMessageForEachState((jobState) -> jobTracker.trackDiscover(JOB_ID, UUID1, null, jobState), metadata, false);
  }

  @Test
  void testTrackSync() throws ConfigNotFoundException, IOException, JsonValidationException {
    testAsynchronous(ConfigType.SYNC, SYNC_CONFIG_METADATA);
  }

  @Test
  void testTrackReset() throws ConfigNotFoundException, IOException, JsonValidationException {
    testAsynchronous(ConfigType.RESET_CONNECTION);
  }

  void testAsynchronous(ConfigType configType) throws ConfigNotFoundException, IOException, JsonValidationException {
    testAsynchronous(configType, Collections.emptyMap());
  }

  // todo update with connection-specific test
  void testAsynchronous(ConfigType configType, Map<String, Object> additionalExpectedMetadata)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // for sync the job id is a long not a uuid.
    final long jobId = 10L;
    when(workspaceHelper.getWorkspaceForJobIdIgnoreExceptions(jobId)).thenReturn(WORKSPACE_ID);

    final ImmutableMap<String, Object> metadata = getJobMetadata(configType, jobId);
    final Job job = getJobMock(configType, jobId);
    // test when frequency is manual.
    when(configRepository.getStandardSync(CONNECTION_ID)).thenReturn(new StandardSync().withConnectionId(CONNECTION_ID).withManual(true));
    final Map<String, Object> manualMetadata = MoreMaps.merge(
        metadata,
        ImmutableMap.of("frequency", "manual"),
        additionalExpectedMetadata);
    assertCorrectMessageForEachState((jobState) -> jobTracker.trackSync(job, jobState), manualMetadata);

    // test when frequency is scheduled.
    when(configRepository.getStandardSync(CONNECTION_ID))
        .thenReturn(new StandardSync().withConnectionId(CONNECTION_ID).withManual(false)
            .withSchedule(new Schedule().withUnits(1L).withTimeUnit(TimeUnit.MINUTES)));
    final Map<String, Object> scheduledMetadata = MoreMaps.merge(
        metadata,
        ImmutableMap.of("frequency", "1 min"),
        additionalExpectedMetadata);
    assertCorrectMessageForEachState((jobState) -> jobTracker.trackSync(job, jobState), scheduledMetadata);
  }

  @Test
  void testTrackSyncAttempt() throws ConfigNotFoundException, IOException, JsonValidationException {
    testAsynchronousAttempt(ConfigType.SYNC, SYNC_CONFIG_METADATA);
  }

  @Test
  void testTrackResetAttempt() throws ConfigNotFoundException, IOException, JsonValidationException {
    testAsynchronousAttempt(ConfigType.RESET_CONNECTION);
  }

  @Test
  void testConfigToMetadata() throws IOException {
    String configJson = MoreResources.readResource("example_config.json");
    JsonNode config = Jsons.deserialize(configJson);

    Map<String, Object> expected = ImmutableMap.of(
        JobTracker.CONFIG + ".username", JobTracker.SET,
        JobTracker.CONFIG + ".has_ssl", false,
        JobTracker.CONFIG + ".password", JobTracker.SET,
        JobTracker.CONFIG + ".one_of.some_key", JobTracker.SET);

    Map<String, Object> actual = JobTracker.configToMetadata(JobTracker.CONFIG, config);

    assertEquals(expected, actual);
  }

  void testAsynchronousAttempt(ConfigType configType) throws ConfigNotFoundException, IOException, JsonValidationException {
    testAsynchronousAttempt(configType, Collections.emptyMap());
  }

  void testAsynchronousAttempt(ConfigType configType, Map<String, Object> additionalExpectedMetadata)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // for sync the job id is a long not a uuid.
    final long jobId = 10L;

    final ImmutableMap<String, Object> metadata = getJobMetadata(configType, jobId);
    final Job job = getJobWithAttemptsMock(configType, jobId);
    // test when frequency is manual.
    when(configRepository.getStandardSync(CONNECTION_ID)).thenReturn(new StandardSync().withConnectionId(CONNECTION_ID).withManual(true));
    when(workspaceHelper.getWorkspaceForJobIdIgnoreExceptions(jobId)).thenReturn(WORKSPACE_ID);
    final Map<String, Object> manualMetadata = MoreMaps.merge(
        ATTEMPT_METADATA,
        metadata,
        ImmutableMap.of("frequency", "manual"),
        additionalExpectedMetadata);

    jobTracker.trackSync(job, JobState.SUCCEEDED);
    assertCorrectMessageForSucceededState(manualMetadata);

    jobTracker.trackSync(job, JobState.FAILED);
    assertCorrectMessageForFailedState(manualMetadata);
  }

  private Job getJobMock(ConfigType configType, long jobId) throws ConfigNotFoundException, IOException, JsonValidationException {
    when(configRepository.getSourceDefinitionFromConnection(CONNECTION_ID))
        .thenReturn(new StandardSourceDefinition()
            .withSourceDefinitionId(UUID1)
            .withName(SOURCE_DEF_NAME)
            .withDockerImageTag(CONNECTOR_VERSION));
    when(configRepository.getDestinationDefinitionFromConnection(CONNECTION_ID))
        .thenReturn(new StandardDestinationDefinition()
            .withDestinationDefinitionId(UUID2)
            .withName(DESTINATION_DEF_NAME)
            .withDockerImageTag(CONNECTOR_VERSION));

    when(configRepository.getStandardSourceDefinition(UUID1))
        .thenReturn(new StandardSourceDefinition()
            .withSourceDefinitionId(UUID1)
            .withName(SOURCE_DEF_NAME)
            .withDockerImageTag(CONNECTOR_VERSION));
    when(configRepository.getStandardDestinationDefinition(UUID2))
        .thenReturn(new StandardDestinationDefinition()
            .withDestinationDefinitionId(UUID2)
            .withName(DESTINATION_DEF_NAME)
            .withDockerImageTag(CONNECTOR_VERSION));

    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)));

    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withSourceConfiguration(Jsons.jsonNode(ImmutableMap.of("key", "some_value")))
        .withDestinationConfiguration(Jsons.jsonNode(ImmutableMap.of("key", false)))
        .withConfiguredAirbyteCatalog(catalog);

    final JobConfig jobConfig = mock(JobConfig.class);
    when(jobConfig.getConfigType()).thenReturn(configType);

    if (configType == ConfigType.SYNC) {
      when(jobConfig.getSync()).thenReturn(jobSyncConfig);
    }

    final Job job = mock(Job.class);
    when(job.getId()).thenReturn(jobId);
    when(job.getConfig()).thenReturn(jobConfig);
    when(job.getConfigType()).thenReturn(configType);
    when(job.getScope()).thenReturn(CONNECTION_ID.toString());
    when(job.getAttemptsCount()).thenReturn(700);
    return job;
  }

  private Job getJobWithAttemptsMock(ConfigType configType, long jobId) throws ConfigNotFoundException, IOException, JsonValidationException {
    final Job job = getJobMock(configType, jobId);
    final Attempt attempt = mock(Attempt.class);
    final JobOutput jobOutput = mock(JobOutput.class);
    final StandardSyncOutput syncOutput = mock(StandardSyncOutput.class);
    final StandardSyncSummary syncSummary = mock(StandardSyncSummary.class);

    when(syncSummary.getStartTime()).thenReturn(SYNC_START_TIME);
    when(syncSummary.getEndTime()).thenReturn(SYNC_END_TIME);
    when(syncSummary.getBytesSynced()).thenReturn(SYNC_BYTES_SYNC);
    when(syncSummary.getRecordsSynced()).thenReturn(SYNC_RECORDS_SYNC);
    when(syncOutput.getStandardSyncSummary()).thenReturn(syncSummary);
    when(jobOutput.getSync()).thenReturn(syncOutput);
    when(attempt.getOutput()).thenReturn(java.util.Optional.of(jobOutput));
    when(job.getAttempts()).thenReturn(List.of(attempt));
    when(jobPersistence.getJob(jobId)).thenReturn(job);
    return job;
  }

  private ImmutableMap<String, Object> getJobMetadata(ConfigType configType, long jobId) {
    return ImmutableMap.<String, Object>builder()
        .put("job_type", configType)
        .put("job_id", String.valueOf(jobId))
        .put("attempt_id", 700)
        .put("connection_id", CONNECTION_ID)
        .put("connector_source", SOURCE_DEF_NAME)
        .put("connector_source_definition_id", UUID1)
        .put("connector_source_version", CONNECTOR_VERSION)
        .put("connector_destination", DESTINATION_DEF_NAME)
        .put("connector_destination_definition_id", UUID2)
        .put("connector_destination_version", CONNECTOR_VERSION)
        .put("namespace_definition", NamespaceDefinitionType.SOURCE)
        .put("table_prefix", false)
        .put("operation_count", 0)
        .build();
  }

  private void assertCheckConnCorrectMessageForEachState(BiConsumer<JobState, StandardCheckConnectionOutput> jobStateConsumer,
                                                         Map<String, Object> metadata,
                                                         boolean workspaceSet) {
    reset(trackingClient);

    // Output does not exist when job has started.
    jobStateConsumer.accept(JobState.STARTED, null);

    final var successOutput = new StandardCheckConnectionOutput();
    successOutput.setStatus(Status.SUCCEEDED);
    jobStateConsumer.accept(JobState.SUCCEEDED, successOutput);
    ImmutableMap<String, Object> checkConnSuccessMetadata = ImmutableMap.of("check_connection_outcome", "succeeded");

    final var failureOutput = new StandardCheckConnectionOutput();
    failureOutput.setStatus(Status.FAILED);
    jobStateConsumer.accept(JobState.SUCCEEDED, failureOutput);
    ImmutableMap<String, Object> checkConnFailureMetadata = ImmutableMap.of("check_connection_outcome", "failed");

    // Failure implies the job threw an exception which almost always meant no output.
    jobStateConsumer.accept(JobState.FAILED, null);
    if (workspaceSet) {
      assertCorrectMessageForStartedState(metadata);
      assertCorrectMessageForSucceededState(MoreMaps.merge(metadata, checkConnSuccessMetadata));
      assertCorrectMessageForSucceededState(MoreMaps.merge(metadata, checkConnFailureMetadata));
      assertCorrectMessageForFailedState(metadata);
    } else {
      verifyNoInteractions(trackingClient);
    }
  }

  private void assertCorrectMessageForEachState(Consumer<JobState> jobStateConsumer, Map<String, Object> expectedMetadata) {
    assertCorrectMessageForEachState(jobStateConsumer, expectedMetadata, true);
  }

  /**
   * Tests that the tracker emits the correct message for when the job starts, succeeds, and fails.
   *
   * @param jobStateConsumer - consumer that takes in a job state and then calls the relevant method
   *        on the job tracker with it. if testing discover, it calls trackDiscover, etc.
   * @param expectedMetadata - expected metadata (except job state).
   */
  private void assertCorrectMessageForEachState(Consumer<JobState> jobStateConsumer, Map<String, Object> expectedMetadata, boolean workspaceSet) {
    jobStateConsumer.accept(JobState.STARTED);
    assertCorrectMessageForStartedState(expectedMetadata);
    jobStateConsumer.accept(JobState.SUCCEEDED);
    assertCorrectMessageForSucceededState(expectedMetadata);
    jobStateConsumer.accept(JobState.FAILED);
    assertCorrectMessageForFailedState(expectedMetadata);
  }

  private void assertCorrectMessageForStartedState(Map<String, Object> metadata) {
    verify(trackingClient).track(WORKSPACE_ID, JobTracker.MESSAGE_NAME, MoreMaps.merge(metadata, STARTED_STATE_METADATA));
  }

  private void assertCorrectMessageForSucceededState(Map<String, Object> metadata) {
    verify(trackingClient).track(WORKSPACE_ID, JobTracker.MESSAGE_NAME, MoreMaps.merge(metadata, SUCCEEDED_STATE_METADATA));
  }

  private void assertCorrectMessageForFailedState(Map<String, Object> metadata) {
    verify(trackingClient).track(WORKSPACE_ID, JobTracker.MESSAGE_NAME, MoreMaps.merge(metadata, FAILED_STATE_METADATA));
  }

}
