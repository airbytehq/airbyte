/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_tracker;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.reset;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.ImmutableMap;
import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.map.MoreMaps;
import io.airbyte.commons.resources.MoreResources;
import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.FailureReason;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.Metadata;
import io.airbyte.config.Schedule;
import io.airbyte.config.Schedule.TimeUnit;
import io.airbyte.config.StandardCheckConnectionOutput;
import io.airbyte.config.StandardCheckConnectionOutput.Status;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.StandardSyncSummary;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.SyncMode;
import io.airbyte.scheduler.models.Attempt;
import io.airbyte.scheduler.models.Job;
import io.airbyte.scheduler.persistence.JobPersistence;
import io.airbyte.scheduler.persistence.WorkspaceHelper;
import io.airbyte.scheduler.persistence.job_tracker.JobTracker.JobState;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import java.util.function.BiConsumer;
import java.util.function.Consumer;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

@SuppressWarnings("PMD.JUnitTestsShouldIncludeAssert")
class JobTrackerTest {

  private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final String WORKSPACE_NAME = "WORKSPACE_TEST";
  private static final UUID JOB_ID = UUID.randomUUID();
  private static final UUID UUID1 = UUID.randomUUID();
  private static final UUID UUID2 = UUID.randomUUID();
  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final String SOURCE_DEF_NAME = "postgres";
  private static final String DESTINATION_DEF_NAME = "bigquery";
  private static final String CONNECTOR_REPOSITORY = "test/test";
  private static final String CONNECTOR_VERSION = "test";
  private static final long SYNC_START_TIME = 1000L;
  private static final long SYNC_END_TIME = 10000L;
  private static final long SYNC_DURATION = 9L; // in sync between end and start time
  private static final long SYNC_BYTES_SYNC = 42L;
  private static final long SYNC_RECORDS_SYNC = 4L;
  private static final long LONG_JOB_ID = 10L; // for sync the job id is a long not a uuid.

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
      .put("sync_start_time", SYNC_START_TIME)
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

  private static final ConnectorSpecification SOURCE_SPEC;
  private static final ConnectorSpecification DESTINATION_SPEC;

  static {
    try {
      SOURCE_SPEC = new ConnectorSpecification().withConnectionSpecification(OBJECT_MAPPER.readTree(
          """
          {
            "type": "object",
            "properties": {
              "key": {
                "type": "string"
              }
            }
          }
          """));
      DESTINATION_SPEC = new ConnectorSpecification().withConnectionSpecification(OBJECT_MAPPER.readTree(
          """
          {
            "type": "object",
            "properties": {
              "key": {
                "type": "boolean"
              }
            }
          }
          """));
    } catch (final JsonProcessingException e) {
      throw new RuntimeException(e);
    }
  }

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
        .put("connector_source_docker_repository", CONNECTOR_REPOSITORY)
        .put("connector_source_version", CONNECTOR_VERSION)
        .build();

    when(configRepository.getStandardSourceDefinition(UUID1))
        .thenReturn(new StandardSourceDefinition()
            .withSourceDefinitionId(UUID1)
            .withName(SOURCE_DEF_NAME)
            .withDockerRepository(CONNECTOR_REPOSITORY)
            .withDockerImageTag(CONNECTOR_VERSION));
    when(configRepository.getStandardWorkspace(WORKSPACE_ID, true))
        .thenReturn(new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withName(WORKSPACE_NAME));
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
        .put("connector_destination_docker_repository", CONNECTOR_REPOSITORY)
        .put("connector_destination_version", CONNECTOR_VERSION)
        .build();

    when(configRepository.getStandardDestinationDefinition(UUID2))
        .thenReturn(new StandardDestinationDefinition()
            .withDestinationDefinitionId(UUID2)
            .withName(DESTINATION_DEF_NAME)
            .withDockerRepository(CONNECTOR_REPOSITORY)
            .withDockerImageTag(CONNECTOR_VERSION));
    when(configRepository.getStandardWorkspace(WORKSPACE_ID, true))
        .thenReturn(new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withName(WORKSPACE_NAME));
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
        .put("connector_source_docker_repository", CONNECTOR_REPOSITORY)
        .put("connector_source_version", CONNECTOR_VERSION)
        .build();

    when(configRepository.getStandardSourceDefinition(UUID1))
        .thenReturn(new StandardSourceDefinition()
            .withSourceDefinitionId(UUID1)
            .withName(SOURCE_DEF_NAME)
            .withDockerRepository(CONNECTOR_REPOSITORY)
            .withDockerImageTag(CONNECTOR_VERSION));
    when(configRepository.getStandardWorkspace(WORKSPACE_ID, true))
        .thenReturn(new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withName(WORKSPACE_NAME));
    assertCorrectMessageForEachState((jobState) -> jobTracker.trackDiscover(JOB_ID, UUID1, WORKSPACE_ID, jobState), metadata);
    assertCorrectMessageForEachState((jobState) -> jobTracker.trackDiscover(JOB_ID, UUID1, null, jobState), metadata);
  }

  @Test
  void testTrackSync() throws ConfigNotFoundException, IOException, JsonValidationException {
    testAsynchronous(ConfigType.SYNC, SYNC_CONFIG_METADATA);
  }

  @Test
  void testTrackReset() throws ConfigNotFoundException, IOException, JsonValidationException {
    testAsynchronous(ConfigType.RESET_CONNECTION);
  }

  void testAsynchronous(final ConfigType configType) throws ConfigNotFoundException, IOException, JsonValidationException {
    testAsynchronous(configType, Collections.emptyMap());
  }

  // todo update with connection-specific test
  void testAsynchronous(final ConfigType configType, final Map<String, Object> additionalExpectedMetadata)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    // for sync the job id is a long not a uuid.
    final long jobId = 10L;
    when(workspaceHelper.getWorkspaceForJobIdIgnoreExceptions(jobId)).thenReturn(WORKSPACE_ID);

    final ImmutableMap<String, Object> metadata = getJobMetadata(configType, jobId);
    final Job job = getJobMock(configType, jobId);
    // test when frequency is manual.
    when(configRepository.getStandardSync(CONNECTION_ID)).thenReturn(new StandardSync().withConnectionId(CONNECTION_ID).withManual(true));
    when(configRepository.getStandardWorkspace(WORKSPACE_ID, true))
        .thenReturn(new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withName(WORKSPACE_NAME));
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
  void testTrackSyncAttemptWithFailures() throws ConfigNotFoundException, IOException, JsonValidationException {
    testAsynchronousAttemptWithFailures(ConfigType.SYNC, SYNC_CONFIG_METADATA);
  }

  @Test
  void testConfigToMetadata() throws IOException {
    final String configJson = MoreResources.readResource("example_config.json");
    final JsonNode config = Jsons.deserialize(configJson);

    final String schemaJson = MoreResources.readResource("example_config_schema.json");
    final JsonNode schema = Jsons.deserialize(schemaJson);

    final Map<String, Object> expected = new ImmutableMap.Builder<String, Object>()
        .put(JobTracker.CONFIG + ".username", JobTracker.SET)
        .put(JobTracker.CONFIG + ".has_ssl", false)
        .put(JobTracker.CONFIG + ".password", JobTracker.SET)
        .put(JobTracker.CONFIG + ".one_of.type_key", "foo")
        .put(JobTracker.CONFIG + ".one_of.some_key", JobTracker.SET)
        .put(JobTracker.CONFIG + ".const_object.sub_key", "bar")
        .put(JobTracker.CONFIG + ".const_object.sub_array", "[1,2,3]")
        .put(JobTracker.CONFIG + ".const_object.sub_object.sub_sub_key", "baz")
        .put(JobTracker.CONFIG + ".enum_string", "foo")
        .put(JobTracker.CONFIG + ".additionalPropertiesUnset.foo", JobTracker.SET)
        .put(JobTracker.CONFIG + ".additionalPropertiesBoolean.foo", JobTracker.SET)
        .put(JobTracker.CONFIG + ".additionalPropertiesSchema.foo", JobTracker.SET)
        .put(JobTracker.CONFIG + ".additionalPropertiesConst.foo", 42)
        .put(JobTracker.CONFIG + ".additionalPropertiesEnumString", "foo")
        .build();

    final Map<String, Object> actual = JobTracker.configToMetadata(JobTracker.CONFIG, config, schema);

    assertEquals(expected, actual);
  }

  void testAsynchronousAttempt(final ConfigType configType) throws ConfigNotFoundException, IOException, JsonValidationException {
    testAsynchronousAttempt(configType, getJobWithAttemptsMock(configType, LONG_JOB_ID), Collections.emptyMap());
  }

  void testAsynchronousAttempt(final ConfigType configType, final Map<String, Object> additionalExpectedMetadata)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    testAsynchronousAttempt(configType, getJobWithAttemptsMock(configType, LONG_JOB_ID), additionalExpectedMetadata);
  }

  void testAsynchronousAttemptWithFailures(final ConfigType configType, final Map<String, Object> additionalExpectedMetadata)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final LinkedHashMap<String, Object> linkedHashMap = new LinkedHashMap<>();
    linkedHashMap.put("failureOrigin", "source");
    linkedHashMap.put("failureType", "config_error");
    linkedHashMap.put("internalMessage", "Internal config error error msg");
    linkedHashMap.put("externalMessage", "Config error related msg");
    linkedHashMap.put("metadata", ImmutableMap.of("some", "metadata"));
    linkedHashMap.put("retryable", true);
    linkedHashMap.put("timestamp", 1010);
    final JsonNode configFailureJson = Jsons.jsonNode(linkedHashMap);

    final LinkedHashMap<String, Object> linkedHashMap1 = new LinkedHashMap<>();
    linkedHashMap1.put("failureOrigin", "replication");
    linkedHashMap1.put("failureType", "system_error");
    linkedHashMap1.put("internalMessage", "Internal system error error msg");
    linkedHashMap1.put("externalMessage", "System error related msg");
    linkedHashMap1.put("metadata", ImmutableMap.of("some", "metadata"));
    linkedHashMap1.put("retryable", true);
    linkedHashMap1.put("timestamp", 1100);
    final JsonNode systemFailureJson = Jsons.jsonNode(linkedHashMap1);

    final LinkedHashMap<String, Object> linkedHashMap2 = new LinkedHashMap<>();
    linkedHashMap2.put("failureOrigin", null);
    linkedHashMap2.put("failureType", null);
    linkedHashMap2.put("internalMessage", "Internal unknown error error msg");
    linkedHashMap2.put("externalMessage", "Unknown error related msg");
    linkedHashMap2.put("metadata", ImmutableMap.of("some", "metadata"));
    linkedHashMap2.put("retryable", true);
    linkedHashMap2.put("timestamp", 1110);
    final JsonNode unknownFailureJson = Jsons.jsonNode(linkedHashMap2);

    final Map<String, Object> failureMetadata = ImmutableMap.of(
        "failure_reasons", Jsons.arrayNode().addAll(Arrays.asList(configFailureJson, systemFailureJson, unknownFailureJson)).toString(),
        "main_failure_reason", configFailureJson.toString());
    testAsynchronousAttempt(configType, getJobWithFailuresMock(configType, LONG_JOB_ID),
        MoreMaps.merge(additionalExpectedMetadata, failureMetadata));
  }

  void testAsynchronousAttempt(final ConfigType configType, final Job job, final Map<String, Object> additionalExpectedMetadata)
      throws ConfigNotFoundException, IOException, JsonValidationException {

    final ImmutableMap<String, Object> metadata = getJobMetadata(configType, LONG_JOB_ID);
    // test when frequency is manual.
    when(configRepository.getStandardSync(CONNECTION_ID)).thenReturn(new StandardSync().withConnectionId(CONNECTION_ID).withManual(true));
    when(workspaceHelper.getWorkspaceForJobIdIgnoreExceptions(LONG_JOB_ID)).thenReturn(WORKSPACE_ID);
    when(configRepository.getStandardWorkspace(WORKSPACE_ID, true))
        .thenReturn(new StandardWorkspace().withWorkspaceId(WORKSPACE_ID).withName(WORKSPACE_NAME));
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

  private Job getJobMock(final ConfigType configType, final long jobId) throws ConfigNotFoundException, IOException, JsonValidationException {
    when(configRepository.getSourceDefinitionFromConnection(CONNECTION_ID))
        .thenReturn(new StandardSourceDefinition()
            .withSourceDefinitionId(UUID1)
            .withName(SOURCE_DEF_NAME)
            .withDockerRepository(CONNECTOR_REPOSITORY)
            .withDockerImageTag(CONNECTOR_VERSION)
            .withSpec(SOURCE_SPEC));
    when(configRepository.getDestinationDefinitionFromConnection(CONNECTION_ID))
        .thenReturn(new StandardDestinationDefinition()
            .withDestinationDefinitionId(UUID2)
            .withName(DESTINATION_DEF_NAME)
            .withDockerRepository(CONNECTOR_REPOSITORY)
            .withDockerImageTag(CONNECTOR_VERSION)
            .withSpec(DESTINATION_SPEC));

    when(configRepository.getStandardSourceDefinition(UUID1))
        .thenReturn(new StandardSourceDefinition()
            .withSourceDefinitionId(UUID1)
            .withName(SOURCE_DEF_NAME)
            .withDockerRepository(CONNECTOR_REPOSITORY)
            .withDockerImageTag(CONNECTOR_VERSION)
            .withSpec(SOURCE_SPEC));
    when(configRepository.getStandardDestinationDefinition(UUID2))
        .thenReturn(new StandardDestinationDefinition()
            .withDestinationDefinitionId(UUID2)
            .withName(DESTINATION_DEF_NAME)
            .withDockerRepository(CONNECTOR_REPOSITORY)
            .withDockerImageTag(CONNECTOR_VERSION)
            .withSpec(DESTINATION_SPEC));

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

  private Attempt getAttemptMock() {
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
    return attempt;
  }

  private Job getJobWithAttemptsMock(final ConfigType configType, final long jobId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return getJobWithAttemptsMock(configType, jobId, List.of(getAttemptMock()));
  }

  private Job getJobWithAttemptsMock(final ConfigType configType, final long jobId, final List<Attempt> attempts)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    final Job job = getJobMock(configType, jobId);
    when(job.getAttempts()).thenReturn(attempts);
    when(jobPersistence.getJob(jobId)).thenReturn(job);
    return job;
  }

  private List<Attempt> getAttemptsWithFailuresMock() {
    final Attempt attemptWithSingleFailure = getAttemptMock();
    final AttemptFailureSummary singleFailureSummary = mock(AttemptFailureSummary.class);
    final FailureReason configFailureReason = new FailureReason()
        .withFailureOrigin(FailureReason.FailureOrigin.SOURCE)
        .withFailureType(FailureReason.FailureType.CONFIG_ERROR)
        .withRetryable(true)
        .withMetadata(new Metadata().withAdditionalProperty("some", "metadata"))
        .withExternalMessage("Config error related msg")
        .withInternalMessage("Internal config error error msg")
        .withStacktrace("Don't include stacktrace in call to track")
        .withTimestamp(SYNC_START_TIME + 10);
    when(singleFailureSummary.getFailures()).thenReturn(List.of(configFailureReason));
    when(attemptWithSingleFailure.getFailureSummary()).thenReturn(Optional.of(singleFailureSummary));

    final Attempt attemptWithMultipleFailures = getAttemptMock();
    final AttemptFailureSummary multipleFailuresSummary = mock(AttemptFailureSummary.class);
    final FailureReason systemFailureReason = new FailureReason()
        .withFailureOrigin(FailureReason.FailureOrigin.REPLICATION)
        .withFailureType(FailureReason.FailureType.SYSTEM_ERROR)
        .withRetryable(true)
        .withMetadata(new Metadata().withAdditionalProperty("some", "metadata"))
        .withExternalMessage("System error related msg")
        .withInternalMessage("Internal system error error msg")
        .withStacktrace("Don't include stacktrace in call to track")
        .withTimestamp(SYNC_START_TIME + 100);
    final FailureReason unknownFailureReason = new FailureReason()
        .withRetryable(true)
        .withMetadata(new Metadata().withAdditionalProperty("some", "metadata"))
        .withExternalMessage("Unknown error related msg")
        .withInternalMessage("Internal unknown error error msg")
        .withStacktrace("Don't include stacktrace in call to track")
        .withTimestamp(SYNC_START_TIME + 110);
    when(multipleFailuresSummary.getFailures()).thenReturn(List.of(systemFailureReason, unknownFailureReason));
    when(attemptWithMultipleFailures.getFailureSummary()).thenReturn(Optional.of(multipleFailuresSummary));

    final Attempt attemptWithNoFailures = getAttemptMock();
    when(attemptWithNoFailures.getFailureSummary()).thenReturn(Optional.empty());

    // in non-test cases we shouldn't actually get failures out of order chronologically
    // this is to verify that we are explicitly sorting the results with tracking failure metadata
    return List.of(attemptWithMultipleFailures, attemptWithSingleFailure, attemptWithNoFailures);
  }

  private Job getJobWithFailuresMock(final ConfigType configType, final long jobId)
      throws ConfigNotFoundException, IOException, JsonValidationException {
    return getJobWithAttemptsMock(configType, jobId, getAttemptsWithFailuresMock());
  }

  private ImmutableMap<String, Object> getJobMetadata(final ConfigType configType, final long jobId) {
    return ImmutableMap.<String, Object>builder()
        .put("job_type", configType)
        .put("job_id", String.valueOf(jobId))
        .put("attempt_id", 700)
        .put("connection_id", CONNECTION_ID)
        .put("connector_source", SOURCE_DEF_NAME)
        .put("connector_source_definition_id", UUID1)
        .put("connector_source_docker_repository", CONNECTOR_REPOSITORY)
        .put("connector_source_version", CONNECTOR_VERSION)
        .put("connector_destination", DESTINATION_DEF_NAME)
        .put("connector_destination_definition_id", UUID2)
        .put("connector_destination_docker_repository", CONNECTOR_REPOSITORY)
        .put("connector_destination_version", CONNECTOR_VERSION)
        .put("namespace_definition", NamespaceDefinitionType.SOURCE)
        .put("table_prefix", false)
        .put("operation_count", 0)
        .build();
  }

  private void assertCheckConnCorrectMessageForEachState(final BiConsumer<JobState, StandardCheckConnectionOutput> jobStateConsumer,
                                                         final Map<String, Object> metadata,
                                                         final boolean workspaceSet) {
    reset(trackingClient);

    // Output does not exist when job has started.
    jobStateConsumer.accept(JobState.STARTED, null);

    final var successOutput = new StandardCheckConnectionOutput();
    successOutput.setStatus(Status.SUCCEEDED);
    jobStateConsumer.accept(JobState.SUCCEEDED, successOutput);
    final ImmutableMap<String, Object> checkConnSuccessMetadata = ImmutableMap.of("check_connection_outcome", "succeeded");

    final var failureOutput = new StandardCheckConnectionOutput();
    failureOutput.setStatus(Status.FAILED);
    jobStateConsumer.accept(JobState.SUCCEEDED, failureOutput);
    final ImmutableMap<String, Object> checkConnFailureMetadata = ImmutableMap.of("check_connection_outcome", "failed");

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

  /**
   * Tests that the tracker emits the correct message for when the job starts, succeeds, and fails.
   *
   * @param jobStateConsumer - consumer that takes in a job state and then calls the relevant method
   *        on the job tracker with it. if testing discover, it calls trackDiscover, etc.
   * @param expectedMetadata - expected metadata (except job state).
   */
  private void assertCorrectMessageForEachState(final Consumer<JobState> jobStateConsumer,
                                                final Map<String, Object> expectedMetadata) {
    jobStateConsumer.accept(JobState.STARTED);
    assertCorrectMessageForStartedState(expectedMetadata);
    jobStateConsumer.accept(JobState.SUCCEEDED);
    assertCorrectMessageForSucceededState(expectedMetadata);
    jobStateConsumer.accept(JobState.FAILED);
    assertCorrectMessageForFailedState(expectedMetadata);
  }

  private void assertCorrectMessageForStartedState(final Map<String, Object> metadata) {
    verify(trackingClient).track(WORKSPACE_ID, JobTracker.MESSAGE_NAME, MoreMaps.merge(metadata, STARTED_STATE_METADATA, mockWorkspaceInfo()));
  }

  private void assertCorrectMessageForSucceededState(final Map<String, Object> metadata) {
    verify(trackingClient).track(WORKSPACE_ID, JobTracker.MESSAGE_NAME, MoreMaps.merge(metadata, SUCCEEDED_STATE_METADATA, mockWorkspaceInfo()));
  }

  private void assertCorrectMessageForFailedState(final Map<String, Object> metadata) {
    verify(trackingClient).track(WORKSPACE_ID, JobTracker.MESSAGE_NAME, MoreMaps.merge(metadata, FAILED_STATE_METADATA, mockWorkspaceInfo()));
  }

  private Map<String, Object> mockWorkspaceInfo() {
    final Map<String, Object> map = new HashMap<>();
    map.put("workspace_id", WORKSPACE_ID);
    map.put("workspace_name", WORKSPACE_NAME);
    return map;
  }

}
