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
  private static final String WORKSPACE_URL = "http://localhost:8000/workspace/my_workspace";
  private static final DeploymentMode DEPLOYMENT_MODE = DeploymentMode.OSS;
  private static final String AIRBYTE_VERSION = "0.1.40";
  private static final String NORMALIZATION_IMAGE = "airbyte/normalization";
  private static final String NORMALIZATION_VERSION = "0.2.18";
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
  private static final String FROM_TRACE_MESSAGE = "from_trace_message";
  private static final String JOB_ID_KEY = "job_id";
  private static final String WORKSPACE_ID_KEY = "workspace_id";
  private static final String WORKSPACE_URL_KEY = "workspace_url";
  private static final String CONNECTION_ID_KEY = "connection_id";
  private static final String CONNECTION_URL_KEY = "connection_url";
  private static final String DEPLOYMENT_MODE_KEY = "deployment_mode";
  private static final String AIRBYTE_VERSION_KEY = "airbyte_version";
  private static final String FAILURE_ORIGIN_KEY = "failure_origin";
  private static final String SOURCE = "source";
  private static final String PREFIX_FORMAT_STRING = "%s_%s";
  private static final String FAILURE_TYPE_KEY = "failure_type";
  private static final String SYSTEM_ERROR = "system_error";
  private static final String CONNECTOR_DEFINITION_ID_KEY = "connector_definition_id";
  private static final String CONNECTOR_REPOSITORY_KEY = "connector_repository";
  private static final String CONNECTOR_NAME_KEY = "connector_name";
  private static final String CONNECTOR_RELEASE_STAGE_KEY = "connector_release_stage";
  private static final String CONNECTOR_COMMAND_KEY = "connector_command";
  private static final String NORMALIZATION_REPOSITORY_KEY = "normalization_repository";

  private ConfigRepository configRepository;
  private JobErrorReportingClient jobErrorReportingClient;
  private WebUrlHelper webUrlHelper;
  private JobErrorReporter jobErrorReporter;

  @BeforeEach
  void setup() {
    configRepository = mock(ConfigRepository.class);
    jobErrorReportingClient = mock(JobErrorReportingClient.class);
    webUrlHelper = mock(WebUrlHelper.class);
    jobErrorReporter = new JobErrorReporter(
        configRepository, DEPLOYMENT_MODE, AIRBYTE_VERSION, NORMALIZATION_IMAGE, NORMALIZATION_VERSION, webUrlHelper, jobErrorReportingClient);

    Mockito.when(webUrlHelper.getConnectionUrl(WORKSPACE_ID, CONNECTION_ID)).thenReturn(CONNECTION_URL);
    Mockito.when(webUrlHelper.getWorkspaceUrl(WORKSPACE_ID)).thenReturn(WORKSPACE_URL);
  }

  @Test
  void testReportSyncJobFailure() {
    final AttemptFailureSummary mFailureSummary = Mockito.mock(AttemptFailureSummary.class);

    final FailureReason sourceFailureReason = new FailureReason()
        .withMetadata(new Metadata()
            .withAdditionalProperty(FROM_TRACE_MESSAGE, true)
            .withAdditionalProperty(CONNECTOR_COMMAND_KEY, "read"))
        .withFailureOrigin(FailureOrigin.SOURCE)
        .withFailureType(FailureType.SYSTEM_ERROR);

    final FailureReason destinationFailureReason = new FailureReason()
        .withMetadata(new Metadata()
            .withAdditionalProperty(FROM_TRACE_MESSAGE, true)
            .withAdditionalProperty(CONNECTOR_COMMAND_KEY, "write"))
        .withFailureOrigin(FailureOrigin.DESTINATION)
        .withFailureType(FailureType.SYSTEM_ERROR);

    final FailureReason normalizationFailureReason = new FailureReason()
        .withMetadata(new Metadata().withAdditionalProperty(FROM_TRACE_MESSAGE, true))
        .withFailureOrigin(FailureOrigin.NORMALIZATION)
        .withFailureType(FailureType.SYSTEM_ERROR);

    final FailureReason nonTraceMessageFailureReason = new FailureReason().withFailureOrigin(FailureOrigin.SOURCE);
    final FailureReason replicationFailureReason = new FailureReason().withFailureOrigin(FailureOrigin.REPLICATION);

    Mockito.when(mFailureSummary.getFailures()).thenReturn(List.of(
        sourceFailureReason, destinationFailureReason, normalizationFailureReason, nonTraceMessageFailureReason, replicationFailureReason));

    final long syncJobId = 1L;
    final SyncJobReportingContext jobReportingContext = new SyncJobReportingContext(
        syncJobId,
        SOURCE_DOCKER_IMAGE,
        DESTINATION_DOCKER_IMAGE);

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
        Map.entry(JOB_ID_KEY, String.valueOf(syncJobId)),
        Map.entry(WORKSPACE_ID_KEY, WORKSPACE_ID.toString()),
        Map.entry(WORKSPACE_URL_KEY, WORKSPACE_URL),
        Map.entry(CONNECTION_ID_KEY, CONNECTION_ID.toString()),
        Map.entry(CONNECTION_URL_KEY, CONNECTION_URL),
        Map.entry(DEPLOYMENT_MODE_KEY, DEPLOYMENT_MODE.name()),
        Map.entry(AIRBYTE_VERSION_KEY, AIRBYTE_VERSION),
        Map.entry(FAILURE_ORIGIN_KEY, SOURCE),
        Map.entry(FAILURE_TYPE_KEY, SYSTEM_ERROR),
        Map.entry(CONNECTOR_COMMAND_KEY, "read"),
        Map.entry(CONNECTOR_DEFINITION_ID_KEY, SOURCE_DEFINITION_ID.toString()),
        Map.entry(CONNECTOR_REPOSITORY_KEY, SOURCE_DOCKER_REPOSITORY),
        Map.entry(CONNECTOR_NAME_KEY, SOURCE_DEFINITION_NAME),
        Map.entry(CONNECTOR_RELEASE_STAGE_KEY, SOURCE_RELEASE_STAGE.toString()));

    final Map<String, String> expectedDestinationMetadata = Map.ofEntries(
        Map.entry(JOB_ID_KEY, String.valueOf(syncJobId)),
        Map.entry(WORKSPACE_ID_KEY, WORKSPACE_ID.toString()),
        Map.entry(WORKSPACE_URL_KEY, WORKSPACE_URL),
        Map.entry(CONNECTION_ID_KEY, CONNECTION_ID.toString()),
        Map.entry(CONNECTION_URL_KEY, CONNECTION_URL),
        Map.entry(DEPLOYMENT_MODE_KEY, DEPLOYMENT_MODE.name()),
        Map.entry(AIRBYTE_VERSION_KEY, AIRBYTE_VERSION),
        Map.entry(FAILURE_ORIGIN_KEY, "destination"),
        Map.entry(FAILURE_TYPE_KEY, SYSTEM_ERROR),
        Map.entry(CONNECTOR_COMMAND_KEY, "write"),
        Map.entry(CONNECTOR_DEFINITION_ID_KEY, DESTINATION_DEFINITION_ID.toString()),
        Map.entry(CONNECTOR_REPOSITORY_KEY, DESTINATION_DOCKER_REPOSITORY),
        Map.entry(CONNECTOR_NAME_KEY, DESTINATION_DEFINITION_NAME),
        Map.entry(CONNECTOR_RELEASE_STAGE_KEY, DESTINATION_RELEASE_STAGE.toString()));

    final Map<String, String> expectedNormalizationMetadata = Map.ofEntries(
        Map.entry(JOB_ID_KEY, String.valueOf(syncJobId)),
        Map.entry(WORKSPACE_ID_KEY, WORKSPACE_ID.toString()),
        Map.entry(WORKSPACE_URL_KEY, WORKSPACE_URL),
        Map.entry(CONNECTION_ID_KEY, CONNECTION_ID.toString()),
        Map.entry(CONNECTION_URL_KEY, CONNECTION_URL),
        Map.entry(DEPLOYMENT_MODE_KEY, DEPLOYMENT_MODE.name()),
        Map.entry(AIRBYTE_VERSION_KEY, AIRBYTE_VERSION),
        Map.entry(FAILURE_ORIGIN_KEY, "normalization"),
        Map.entry(FAILURE_TYPE_KEY, SYSTEM_ERROR),
        Map.entry(NORMALIZATION_REPOSITORY_KEY, NORMALIZATION_IMAGE),
        Map.entry(String.format(PREFIX_FORMAT_STRING, SOURCE, CONNECTOR_DEFINITION_ID_KEY), SOURCE_DEFINITION_ID.toString()),
        Map.entry(String.format(PREFIX_FORMAT_STRING, SOURCE, CONNECTOR_REPOSITORY_KEY), SOURCE_DOCKER_REPOSITORY),
        Map.entry(String.format(PREFIX_FORMAT_STRING, SOURCE, CONNECTOR_NAME_KEY), SOURCE_DEFINITION_NAME),
        Map.entry(String.format(PREFIX_FORMAT_STRING, SOURCE, CONNECTOR_RELEASE_STAGE_KEY), SOURCE_RELEASE_STAGE.toString()),
        Map.entry(CONNECTOR_DEFINITION_ID_KEY, DESTINATION_DEFINITION_ID.toString()),
        Map.entry(CONNECTOR_REPOSITORY_KEY, DESTINATION_DOCKER_REPOSITORY),
        Map.entry(CONNECTOR_NAME_KEY, DESTINATION_DEFINITION_NAME),
        Map.entry(CONNECTOR_RELEASE_STAGE_KEY, DESTINATION_RELEASE_STAGE.toString()));

    Mockito.verify(jobErrorReportingClient).reportJobFailureReason(mWorkspace, sourceFailureReason, SOURCE_DOCKER_IMAGE, expectedSourceMetadata);
    Mockito.verify(jobErrorReportingClient).reportJobFailureReason(mWorkspace, destinationFailureReason, DESTINATION_DOCKER_IMAGE,
        expectedDestinationMetadata);
    Mockito.verify(jobErrorReportingClient).reportJobFailureReason(
        mWorkspace, normalizationFailureReason, String.format("%s:%s", NORMALIZATION_IMAGE, NORMALIZATION_VERSION), expectedNormalizationMetadata);
    Mockito.verifyNoMoreInteractions(jobErrorReportingClient);
  }

  @Test
  void testReportSyncJobFailureDoesNotThrow() {
    final AttemptFailureSummary mFailureSummary = Mockito.mock(AttemptFailureSummary.class);
    final SyncJobReportingContext jobContext = new SyncJobReportingContext(1L, SOURCE_DOCKER_IMAGE, DESTINATION_DOCKER_IMAGE);

    final FailureReason sourceFailureReason = new FailureReason()
        .withMetadata(new Metadata().withAdditionalProperty(FROM_TRACE_MESSAGE, true))
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
    final String connectorCommand = "check";
    final FailureReason failureReason = new FailureReason()
        .withMetadata(new Metadata()
            .withAdditionalProperty(FROM_TRACE_MESSAGE, true)
            .withAdditionalProperty(CONNECTOR_COMMAND_KEY, connectorCommand))
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
        Map.entry(JOB_ID_KEY, JOB_ID.toString()),
        Map.entry(WORKSPACE_ID_KEY, WORKSPACE_ID.toString()),
        Map.entry(WORKSPACE_URL_KEY, WORKSPACE_URL),
        Map.entry(DEPLOYMENT_MODE_KEY, DEPLOYMENT_MODE.name()),
        Map.entry(AIRBYTE_VERSION_KEY, AIRBYTE_VERSION),
        Map.entry(FAILURE_ORIGIN_KEY, SOURCE),
        Map.entry(FAILURE_TYPE_KEY, SYSTEM_ERROR),
        Map.entry(CONNECTOR_DEFINITION_ID_KEY, SOURCE_DEFINITION_ID.toString()),
        Map.entry(CONNECTOR_REPOSITORY_KEY, SOURCE_DOCKER_REPOSITORY),
        Map.entry(CONNECTOR_NAME_KEY, SOURCE_DEFINITION_NAME),
        Map.entry(CONNECTOR_RELEASE_STAGE_KEY, SOURCE_RELEASE_STAGE.toString()),
        Map.entry(CONNECTOR_COMMAND_KEY, connectorCommand));

    Mockito.verify(jobErrorReportingClient).reportJobFailureReason(mWorkspace, failureReason, SOURCE_DOCKER_IMAGE, expectedMetadata);
    Mockito.verifyNoMoreInteractions(jobErrorReportingClient);
  }

  @Test
  void testReportDestinationCheckJobFailure() throws JsonValidationException, ConfigNotFoundException, IOException {
    final String connectorCommand = "check";
    final FailureReason failureReason = new FailureReason()
        .withMetadata(new Metadata()
            .withAdditionalProperty(FROM_TRACE_MESSAGE, true)
            .withAdditionalProperty(CONNECTOR_COMMAND_KEY, connectorCommand))
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
        Map.entry(JOB_ID_KEY, JOB_ID.toString()),
        Map.entry(WORKSPACE_ID_KEY, WORKSPACE_ID.toString()),
        Map.entry(WORKSPACE_URL_KEY, WORKSPACE_URL),
        Map.entry(DEPLOYMENT_MODE_KEY, DEPLOYMENT_MODE.name()),
        Map.entry(AIRBYTE_VERSION_KEY, AIRBYTE_VERSION),
        Map.entry(FAILURE_ORIGIN_KEY, "destination"),
        Map.entry(FAILURE_TYPE_KEY, SYSTEM_ERROR),
        Map.entry(CONNECTOR_DEFINITION_ID_KEY, DESTINATION_DEFINITION_ID.toString()),
        Map.entry(CONNECTOR_REPOSITORY_KEY, DESTINATION_DOCKER_REPOSITORY),
        Map.entry(CONNECTOR_NAME_KEY, DESTINATION_DEFINITION_NAME),
        Map.entry(CONNECTOR_RELEASE_STAGE_KEY, DESTINATION_RELEASE_STAGE.toString()),
        Map.entry(CONNECTOR_COMMAND_KEY, connectorCommand));

    Mockito.verify(jobErrorReportingClient).reportJobFailureReason(mWorkspace, failureReason, DESTINATION_DOCKER_IMAGE, expectedMetadata);
    Mockito.verifyNoMoreInteractions(jobErrorReportingClient);
  }

  @Test
  void testReportDiscoverJobFailure() throws JsonValidationException, ConfigNotFoundException, IOException {
    final FailureReason failureReason = new FailureReason()
        .withMetadata(new Metadata()
            .withAdditionalProperty(FROM_TRACE_MESSAGE, true)
            .withAdditionalProperty(CONNECTOR_COMMAND_KEY, "discover"))
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
        Map.entry(JOB_ID_KEY, JOB_ID.toString()),
        Map.entry(WORKSPACE_ID_KEY, WORKSPACE_ID.toString()),
        Map.entry(WORKSPACE_URL_KEY, WORKSPACE_URL),
        Map.entry(DEPLOYMENT_MODE_KEY, DEPLOYMENT_MODE.name()),
        Map.entry(AIRBYTE_VERSION_KEY, AIRBYTE_VERSION),
        Map.entry(FAILURE_ORIGIN_KEY, SOURCE),
        Map.entry(FAILURE_TYPE_KEY, SYSTEM_ERROR),
        Map.entry(CONNECTOR_DEFINITION_ID_KEY, SOURCE_DEFINITION_ID.toString()),
        Map.entry(CONNECTOR_REPOSITORY_KEY, SOURCE_DOCKER_REPOSITORY),
        Map.entry(CONNECTOR_NAME_KEY, SOURCE_DEFINITION_NAME),
        Map.entry(CONNECTOR_RELEASE_STAGE_KEY, SOURCE_RELEASE_STAGE.toString()),
        Map.entry(CONNECTOR_COMMAND_KEY, "discover"));

    Mockito.verify(jobErrorReportingClient).reportJobFailureReason(mWorkspace, failureReason, SOURCE_DOCKER_IMAGE, expectedMetadata);
    Mockito.verifyNoMoreInteractions(jobErrorReportingClient);
  }

  @Test
  void testReportSpecJobFailure() {
    final FailureReason failureReason = new FailureReason()
        .withMetadata(new Metadata()
            .withAdditionalProperty(FROM_TRACE_MESSAGE, true)
            .withAdditionalProperty(CONNECTOR_COMMAND_KEY, "spec"))
        .withFailureOrigin(FailureOrigin.SOURCE)
        .withFailureType(FailureType.SYSTEM_ERROR);

    final ConnectorJobReportingContext jobContext = new ConnectorJobReportingContext(JOB_ID, SOURCE_DOCKER_IMAGE);

    jobErrorReporter.reportSpecJobFailure(failureReason, jobContext);

    final Map<String, String> expectedMetadata = Map.ofEntries(
        Map.entry(JOB_ID_KEY, JOB_ID.toString()),
        Map.entry(DEPLOYMENT_MODE_KEY, DEPLOYMENT_MODE.name()),
        Map.entry(AIRBYTE_VERSION_KEY, AIRBYTE_VERSION),
        Map.entry(FAILURE_ORIGIN_KEY, SOURCE),
        Map.entry(FAILURE_TYPE_KEY, SYSTEM_ERROR),
        Map.entry(CONNECTOR_REPOSITORY_KEY, SOURCE_DOCKER_REPOSITORY),
        Map.entry(CONNECTOR_COMMAND_KEY, "spec"));

    Mockito.verify(jobErrorReportingClient).reportJobFailureReason(null, failureReason, SOURCE_DOCKER_IMAGE, expectedMetadata);
    Mockito.verifyNoMoreInteractions(jobErrorReportingClient);
  }

}
