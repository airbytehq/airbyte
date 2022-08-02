/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence.job_error_reporter;

import static org.mockito.Mockito.mock;

import io.airbyte.config.AttemptFailureSummary;
import io.airbyte.config.Configs.DeploymentMode;
import io.airbyte.config.FailureReason;
import io.airbyte.config.FailureReason.FailureOrigin;
import io.airbyte.config.FailureReason.FailureType;
import io.airbyte.config.Metadata;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.scheduler.persistence.WebUrlHelper;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

class JobErrorReporterTest {

  private static final UUID JOB_ID = UUID.randomUUID();
  private static final UUID WORKSPACE_ID = UUID.randomUUID();
  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final String CONNECTION_URL = "http://localhost:8000/connection/my_connection";
  private static final DeploymentMode DEPLOYMENT_MODE = DeploymentMode.OSS;
  private static final String AIRBYTE_VERSION = "0.1.40";
  private static final UUID SOURCE_DEFINITION_ID = UUID.randomUUID();
  private static final String SOURCE_DEFINITION_NAME = "stripe";
  private static final String SOURCE_DOCKER_REPOSITORY = "airbyte/source-stripe";
  private static final String SOURCE_DOCKER_IMAGE = "airbyte/source-stripe:1.2.3";
  private static final StandardSourceDefinition.ReleaseStage SOURCE_RELEASE_STAGE = StandardSourceDefinition.ReleaseStage.BETA;
  private static final UUID DESTINATION_DEFINITION_ID = UUID.randomUUID();
  private static final String DESTINATION_DEFINITION_NAME = "snowflake";
  private static final String DESTINATION_DOCKER_REPOSITORY = "airbyte/destination-snowflake";
  private static final String DESTINATION_DOCKER_IMAGE = "airbyte/destination-snowflake:1.2.3";
  private static final StandardDestinationDefinition.ReleaseStage DESTINATION_RELEASE_STAGE = StandardDestinationDefinition.ReleaseStage.BETA;

  private ConfigRepository configRepository;
  private JobErrorReportingClient jobErrorReportingClient;
  private WebUrlHelper webUrlHelper;
  private JobErrorReporter jobErrorReporter;

  @BeforeEach
  void setup() {
    configRepository = mock(ConfigRepository.class);
    jobErrorReportingClient = mock(JobErrorReportingClient.class);
    webUrlHelper = mock(WebUrlHelper.class);
    jobErrorReporter = new JobErrorReporter(configRepository, DEPLOYMENT_MODE, AIRBYTE_VERSION, webUrlHelper, jobErrorReportingClient);
  }

  @Test
  void testReportSyncJobFailure() {
    final AttemptFailureSummary mFailureSummary = Mockito.mock(AttemptFailureSummary.class);

    final FailureReason sourceFailureReason = new FailureReason()
        .withMetadata(new Metadata().withAdditionalProperty("from_trace_message", true))
        .withFailureOrigin(FailureOrigin.SOURCE)
        .withFailureType(FailureType.SYSTEM_ERROR);

    final FailureReason destinationFailureReason = new FailureReason()
        .withMetadata(new Metadata().withAdditionalProperty("from_trace_message", true))
        .withFailureOrigin(FailureOrigin.DESTINATION)
        .withFailureType(FailureType.SYSTEM_ERROR);

    final FailureReason nonTraceMessageFailureReason = new FailureReason().withFailureOrigin(FailureOrigin.SOURCE);
    final FailureReason replicationFailureReason = new FailureReason().withFailureOrigin(FailureOrigin.REPLICATION);

    Mockito.when(mFailureSummary.getFailures())
        .thenReturn(List.of(sourceFailureReason, destinationFailureReason, nonTraceMessageFailureReason, replicationFailureReason));

    final long syncJobId = 1L;
    final SyncJobReportingContext jobReportingContext = new SyncJobReportingContext(
        syncJobId,
        SOURCE_DOCKER_IMAGE,
        DESTINATION_DOCKER_IMAGE);

    Mockito.when(webUrlHelper.getConnectionUrl(WORKSPACE_ID, CONNECTION_ID)).thenReturn(CONNECTION_URL);

    Mockito.when(configRepository.getSourceDefinitionFromConnection(CONNECTION_ID))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPOSITORY)
            .withReleaseStage(SOURCE_RELEASE_STAGE)
            .withSourceDefinitionId(SOURCE_DEFINITION_ID)
            .withName(SOURCE_DEFINITION_NAME));

    Mockito.when(configRepository.getDestinationDefinitionFromConnection(CONNECTION_ID))
        .thenReturn(new StandardDestinationDefinition()
            .withDockerRepository(DESTINATION_DOCKER_REPOSITORY)
            .withReleaseStage(DESTINATION_RELEASE_STAGE)
            .withDestinationDefinitionId(DESTINATION_DEFINITION_ID)
            .withName(DESTINATION_DEFINITION_NAME));

    final StandardWorkspace mWorkspace = Mockito.mock(StandardWorkspace.class);
    Mockito.when(mWorkspace.getWorkspaceId()).thenReturn(WORKSPACE_ID);
    Mockito.when(configRepository.getStandardWorkspaceFromConnection(CONNECTION_ID, true)).thenReturn(mWorkspace);

    jobErrorReporter.reportSyncJobFailure(CONNECTION_ID, mFailureSummary, jobReportingContext);

    final Map<String, String> expectedSourceMetadata = Map.ofEntries(
        Map.entry("job_id", String.valueOf(syncJobId)),
        Map.entry("workspace_id", WORKSPACE_ID.toString()),
        Map.entry("connection_id", CONNECTION_ID.toString()),
        Map.entry("connection_url", CONNECTION_URL),
        Map.entry("deployment_mode", DEPLOYMENT_MODE.name()),
        Map.entry("airbyte_version", AIRBYTE_VERSION),
        Map.entry("failure_origin", "source"),
        Map.entry("failure_type", "system_error"),
        Map.entry("connector_definition_id", SOURCE_DEFINITION_ID.toString()),
        Map.entry("connector_repository", SOURCE_DOCKER_REPOSITORY),
        Map.entry("connector_name", SOURCE_DEFINITION_NAME),
        Map.entry("connector_release_stage", SOURCE_RELEASE_STAGE.toString()));

    final Map<String, String> expectedDestinationMetadata = Map.ofEntries(
        Map.entry("job_id", String.valueOf(syncJobId)),
        Map.entry("workspace_id", WORKSPACE_ID.toString()),
        Map.entry("connection_id", CONNECTION_ID.toString()),
        Map.entry("connection_url", CONNECTION_URL),
        Map.entry("deployment_mode", DEPLOYMENT_MODE.name()),
        Map.entry("airbyte_version", AIRBYTE_VERSION),
        Map.entry("failure_origin", "destination"),
        Map.entry("failure_type", "system_error"),
        Map.entry("connector_definition_id", DESTINATION_DEFINITION_ID.toString()),
        Map.entry("connector_repository", DESTINATION_DOCKER_REPOSITORY),
        Map.entry("connector_name", DESTINATION_DEFINITION_NAME),
        Map.entry("connector_release_stage", DESTINATION_RELEASE_STAGE.toString()));

    Mockito.verify(jobErrorReportingClient).reportJobFailureReason(mWorkspace, sourceFailureReason, SOURCE_DOCKER_IMAGE, expectedSourceMetadata);
    Mockito.verify(jobErrorReportingClient).reportJobFailureReason(mWorkspace, destinationFailureReason, DESTINATION_DOCKER_IMAGE,
        expectedDestinationMetadata);
    Mockito.verifyNoMoreInteractions(jobErrorReportingClient);
  }

  @Test
  void testReportSyncJobFailureDoesNotThrow() {
    final AttemptFailureSummary mFailureSummary = Mockito.mock(AttemptFailureSummary.class);
    final SyncJobReportingContext jobContext = new SyncJobReportingContext(1L, SOURCE_DOCKER_IMAGE, DESTINATION_DOCKER_IMAGE);

    final FailureReason sourceFailureReason = new FailureReason()
        .withMetadata(new Metadata().withAdditionalProperty("from_trace_message", true))
        .withFailureOrigin(FailureOrigin.SOURCE)
        .withFailureType(FailureType.SYSTEM_ERROR);

    Mockito.when(mFailureSummary.getFailures()).thenReturn(List.of(sourceFailureReason));

    Mockito.when(configRepository.getSourceDefinitionFromConnection(CONNECTION_ID))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPOSITORY)
            .withReleaseStage(SOURCE_RELEASE_STAGE)
            .withSourceDefinitionId(SOURCE_DEFINITION_ID)
            .withName(SOURCE_DEFINITION_NAME));

    final StandardWorkspace mWorkspace = Mockito.mock(StandardWorkspace.class);
    Mockito.when(mWorkspace.getWorkspaceId()).thenReturn(WORKSPACE_ID);
    Mockito.when(configRepository.getStandardWorkspaceFromConnection(CONNECTION_ID, true)).thenReturn(mWorkspace);
    Mockito.when(webUrlHelper.getConnectionUrl(WORKSPACE_ID, CONNECTION_ID)).thenReturn(CONNECTION_URL);

    Mockito.doThrow(new RuntimeException("some exception"))
        .when(jobErrorReportingClient)
        .reportJobFailureReason(Mockito.any(), Mockito.eq(sourceFailureReason), Mockito.any(), Mockito.any());

    Assertions.assertDoesNotThrow(() -> jobErrorReporter.reportSyncJobFailure(CONNECTION_ID, mFailureSummary, jobContext));
    Mockito.verify(jobErrorReportingClient, Mockito.times(1))
        .reportJobFailureReason(Mockito.any(), Mockito.any(), Mockito.any(), Mockito.any());
  }

  @Test
  void testReportSourceCheckJobFailure() throws JsonValidationException, ConfigNotFoundException, IOException {
    final FailureReason failureReason = new FailureReason()
        .withMetadata(new Metadata().withAdditionalProperty("from_trace_message", true))
        .withFailureOrigin(FailureOrigin.SOURCE)
        .withFailureType(FailureType.SYSTEM_ERROR);

    final ConnectorJobReportingContext jobContext = new ConnectorJobReportingContext(JOB_ID, SOURCE_DOCKER_IMAGE);

    Mockito.when(configRepository.getStandardSourceDefinition(SOURCE_DEFINITION_ID))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPOSITORY)
            .withReleaseStage(SOURCE_RELEASE_STAGE)
            .withSourceDefinitionId(SOURCE_DEFINITION_ID)
            .withName(SOURCE_DEFINITION_NAME));

    final StandardWorkspace mWorkspace = Mockito.mock(StandardWorkspace.class);
    Mockito.when(mWorkspace.getWorkspaceId()).thenReturn(WORKSPACE_ID);
    Mockito.when(configRepository.getStandardWorkspace(WORKSPACE_ID, true)).thenReturn(mWorkspace);

    jobErrorReporter.reportSourceCheckJobFailure(SOURCE_DEFINITION_ID, WORKSPACE_ID, failureReason, jobContext);

    final Map<String, String> expectedMetadata = Map.ofEntries(
        Map.entry("job_id", JOB_ID.toString()),
        Map.entry("workspace_id", WORKSPACE_ID.toString()),
        Map.entry("deployment_mode", DEPLOYMENT_MODE.name()),
        Map.entry("airbyte_version", AIRBYTE_VERSION),
        Map.entry("failure_origin", "source"),
        Map.entry("failure_type", "system_error"),
        Map.entry("connector_definition_id", SOURCE_DEFINITION_ID.toString()),
        Map.entry("connector_repository", SOURCE_DOCKER_REPOSITORY),
        Map.entry("connector_name", SOURCE_DEFINITION_NAME),
        Map.entry("connector_release_stage", SOURCE_RELEASE_STAGE.toString()),
        Map.entry("connector_command", "check"));

    Mockito.verify(jobErrorReportingClient).reportJobFailureReason(mWorkspace, failureReason, SOURCE_DOCKER_IMAGE, expectedMetadata);
    Mockito.verifyNoMoreInteractions(jobErrorReportingClient);
  }

  @Test
  void testReportDestinationCheckJobFailure() throws JsonValidationException, ConfigNotFoundException, IOException {
    final FailureReason failureReason = new FailureReason()
        .withMetadata(new Metadata().withAdditionalProperty("from_trace_message", true))
        .withFailureOrigin(FailureOrigin.DESTINATION)
        .withFailureType(FailureType.SYSTEM_ERROR);

    final ConnectorJobReportingContext jobContext = new ConnectorJobReportingContext(JOB_ID, DESTINATION_DOCKER_IMAGE);

    Mockito.when(configRepository.getStandardDestinationDefinition(DESTINATION_DEFINITION_ID))
        .thenReturn(new StandardDestinationDefinition()
            .withDockerRepository(DESTINATION_DOCKER_REPOSITORY)
            .withReleaseStage(DESTINATION_RELEASE_STAGE)
            .withDestinationDefinitionId(DESTINATION_DEFINITION_ID)
            .withName(DESTINATION_DEFINITION_NAME));

    final StandardWorkspace mWorkspace = Mockito.mock(StandardWorkspace.class);
    Mockito.when(mWorkspace.getWorkspaceId()).thenReturn(WORKSPACE_ID);
    Mockito.when(configRepository.getStandardWorkspace(WORKSPACE_ID, true)).thenReturn(mWorkspace);

    jobErrorReporter.reportDestinationCheckJobFailure(DESTINATION_DEFINITION_ID, WORKSPACE_ID, failureReason, jobContext);

    final Map<String, String> expectedMetadata = Map.ofEntries(
        Map.entry("job_id", JOB_ID.toString()),
        Map.entry("workspace_id", WORKSPACE_ID.toString()),
        Map.entry("deployment_mode", DEPLOYMENT_MODE.name()),
        Map.entry("airbyte_version", AIRBYTE_VERSION),
        Map.entry("failure_origin", "destination"),
        Map.entry("failure_type", "system_error"),
        Map.entry("connector_definition_id", DESTINATION_DEFINITION_ID.toString()),
        Map.entry("connector_repository", DESTINATION_DOCKER_REPOSITORY),
        Map.entry("connector_name", DESTINATION_DEFINITION_NAME),
        Map.entry("connector_release_stage", DESTINATION_RELEASE_STAGE.toString()),
        Map.entry("connector_command", "check"));

    Mockito.verify(jobErrorReportingClient).reportJobFailureReason(mWorkspace, failureReason, DESTINATION_DOCKER_IMAGE, expectedMetadata);
    Mockito.verifyNoMoreInteractions(jobErrorReportingClient);
  }

  @Test
  void testReportDiscoverJobFailure() throws JsonValidationException, ConfigNotFoundException, IOException {
    final FailureReason failureReason = new FailureReason()
        .withMetadata(new Metadata().withAdditionalProperty("from_trace_message", true))
        .withFailureOrigin(FailureOrigin.SOURCE)
        .withFailureType(FailureType.SYSTEM_ERROR);

    final ConnectorJobReportingContext jobContext = new ConnectorJobReportingContext(JOB_ID, SOURCE_DOCKER_IMAGE);

    Mockito.when(configRepository.getStandardSourceDefinition(SOURCE_DEFINITION_ID))
        .thenReturn(new StandardSourceDefinition()
            .withDockerRepository(SOURCE_DOCKER_REPOSITORY)
            .withReleaseStage(SOURCE_RELEASE_STAGE)
            .withSourceDefinitionId(SOURCE_DEFINITION_ID)
            .withName(SOURCE_DEFINITION_NAME));

    final StandardWorkspace mWorkspace = Mockito.mock(StandardWorkspace.class);
    Mockito.when(mWorkspace.getWorkspaceId()).thenReturn(WORKSPACE_ID);
    Mockito.when(configRepository.getStandardWorkspace(WORKSPACE_ID, true)).thenReturn(mWorkspace);

    jobErrorReporter.reportDiscoverJobFailure(SOURCE_DEFINITION_ID, WORKSPACE_ID, failureReason, jobContext);

    final Map<String, String> expectedMetadata = Map.ofEntries(
        Map.entry("job_id", JOB_ID.toString()),
        Map.entry("workspace_id", WORKSPACE_ID.toString()),
        Map.entry("deployment_mode", DEPLOYMENT_MODE.name()),
        Map.entry("airbyte_version", AIRBYTE_VERSION),
        Map.entry("failure_origin", "source"),
        Map.entry("failure_type", "system_error"),
        Map.entry("connector_definition_id", SOURCE_DEFINITION_ID.toString()),
        Map.entry("connector_repository", SOURCE_DOCKER_REPOSITORY),
        Map.entry("connector_name", SOURCE_DEFINITION_NAME),
        Map.entry("connector_release_stage", SOURCE_RELEASE_STAGE.toString()),
        Map.entry("connector_command", "discover"));

    Mockito.verify(jobErrorReportingClient).reportJobFailureReason(mWorkspace, failureReason, SOURCE_DOCKER_IMAGE, expectedMetadata);
    Mockito.verifyNoMoreInteractions(jobErrorReportingClient);
  }

  @Test
  void testReportSpecJobFailure() {
    final FailureReason failureReason = new FailureReason()
        .withMetadata(new Metadata().withAdditionalProperty("from_trace_message", true))
        .withFailureOrigin(FailureOrigin.SOURCE)
        .withFailureType(FailureType.SYSTEM_ERROR);

    final ConnectorJobReportingContext jobContext = new ConnectorJobReportingContext(JOB_ID, SOURCE_DOCKER_IMAGE);

    jobErrorReporter.reportSpecJobFailure(failureReason, jobContext);

    final Map<String, String> expectedMetadata = Map.ofEntries(
        Map.entry("job_id", JOB_ID.toString()),
        Map.entry("deployment_mode", DEPLOYMENT_MODE.name()),
        Map.entry("airbyte_version", AIRBYTE_VERSION),
        Map.entry("failure_origin", "source"),
        Map.entry("failure_type", "system_error"),
        Map.entry("connector_repository", SOURCE_DOCKER_REPOSITORY),
        Map.entry("connector_command", "spec"));

    Mockito.verify(jobErrorReportingClient).reportJobFailureReason(null, failureReason, SOURCE_DOCKER_IMAGE, expectedMetadata);
    Mockito.verifyNoMoreInteractions(jobErrorReportingClient);
  }

}
