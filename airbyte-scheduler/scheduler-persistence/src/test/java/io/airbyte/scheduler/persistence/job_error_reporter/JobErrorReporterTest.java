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
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.Metadata;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.persistence.ConfigRepository;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

public class JobErrorReporterTest {

  private static final UUID CONNECTION_ID = UUID.randomUUID();
  private static final DeploymentMode DEPLOYMENT_MODE = DeploymentMode.OSS;
  private static final String AIRBYTE_VERSION = "0.1.40";
  private static final UUID SOURCE_DEFINITION_ID = UUID.randomUUID();
  private static final String SOURCE_DEFINITION_NAME = "stripe";
  private static final String SOURCE_DOCKER_IMAGE = "airbyte/source-stripe:1.2.3";
  private static final StandardSourceDefinition.ReleaseStage SOURCE_RELEASE_STAGE = StandardSourceDefinition.ReleaseStage.BETA;
  private static final UUID DESTINATION_DEFINITION_ID = UUID.randomUUID();
  private static final String DESTINATION_DEFINITION_NAME = "snowflake";
  private static final StandardDestinationDefinition.ReleaseStage DESTINATION_RELEASE_STAGE = StandardDestinationDefinition.ReleaseStage.BETA;
  private static final String DESTINATION_DOCKER_IMAGE = "airbyte/destination-snowflake:1.2.3";

  private ConfigRepository configRepository;
  private JobErrorReportingClient jobErrorReportingClient;
  private JobErrorReporter jobErrorReporter;

  @BeforeEach
  void setup() {
    configRepository = mock(ConfigRepository.class);
    jobErrorReportingClient = mock(JobErrorReportingClient.class);
    jobErrorReporter = new JobErrorReporter(configRepository, DEPLOYMENT_MODE, AIRBYTE_VERSION, jobErrorReportingClient);
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

    final JobSyncConfig mJobSyncConfig = Mockito.mock(JobSyncConfig.class);
    Mockito.when(mJobSyncConfig.getSourceDockerImage()).thenReturn(SOURCE_DOCKER_IMAGE);
    Mockito.when(mJobSyncConfig.getDestinationDockerImage()).thenReturn(DESTINATION_DOCKER_IMAGE);

    Mockito.when(configRepository.getSourceDefinitionFromConnection(CONNECTION_ID))
        .thenReturn(new StandardSourceDefinition()
            .withReleaseStage(SOURCE_RELEASE_STAGE)
            .withSourceDefinitionId(SOURCE_DEFINITION_ID)
            .withName(SOURCE_DEFINITION_NAME));

    Mockito.when(configRepository.getDestinationDefinitionFromConnection(CONNECTION_ID))
        .thenReturn(new StandardDestinationDefinition()
            .withReleaseStage(DESTINATION_RELEASE_STAGE)
            .withDestinationDefinitionId(DESTINATION_DEFINITION_ID)
            .withName(DESTINATION_DEFINITION_NAME));

    final StandardWorkspace mWorkspace = Mockito.mock(StandardWorkspace.class);
    Mockito.when(configRepository.getStandardWorkspaceFromConnection(CONNECTION_ID, true)).thenReturn(mWorkspace);

    jobErrorReporter.reportSyncJobFailure(CONNECTION_ID, mFailureSummary, mJobSyncConfig);

    final Map<String, String> expectedSourceMetadata = Map.of(
        "connection_id", CONNECTION_ID.toString(),
        "deployment_mode", DEPLOYMENT_MODE.name(),
        "airbyte_version", AIRBYTE_VERSION,
        "failure_origin", "source",
        "failure_type", "system_error",
        "connector_definition_id", SOURCE_DEFINITION_ID.toString(),
        "connector_name", SOURCE_DEFINITION_NAME,
        "connector_release_stage", SOURCE_RELEASE_STAGE.toString());

    final Map<String, String> expectedDestinationMetadata = Map.of(
        "connection_id", CONNECTION_ID.toString(),
        "deployment_mode", DEPLOYMENT_MODE.name(),
        "airbyte_version", AIRBYTE_VERSION,
        "failure_origin", "destination",
        "failure_type", "system_error",
        "connector_definition_id", DESTINATION_DEFINITION_ID.toString(),
        "connector_name", DESTINATION_DEFINITION_NAME,
        "connector_release_stage", DESTINATION_RELEASE_STAGE.toString());

    Mockito.verify(jobErrorReportingClient).reportJobFailureReason(mWorkspace, sourceFailureReason, SOURCE_DOCKER_IMAGE, expectedSourceMetadata);
    Mockito.verify(jobErrorReportingClient).reportJobFailureReason(mWorkspace, destinationFailureReason, DESTINATION_DOCKER_IMAGE,
        expectedDestinationMetadata);
    Mockito.verifyNoMoreInteractions(jobErrorReportingClient);
  }

  @Test
  void testReportSyncJobFailureDoesNotThrow() {
    final AttemptFailureSummary mFailureSummary = Mockito.mock(AttemptFailureSummary.class);
    final JobSyncConfig mJobSyncConfig = Mockito.mock(JobSyncConfig.class);

    final FailureReason sourceFailureReason = new FailureReason()
        .withMetadata(new Metadata().withAdditionalProperty("from_trace_message", true))
        .withFailureOrigin(FailureOrigin.SOURCE)
        .withFailureType(FailureType.SYSTEM_ERROR);

    Mockito.when(mFailureSummary.getFailures()).thenReturn(List.of(sourceFailureReason));

    Mockito.when(configRepository.getSourceDefinitionFromConnection(CONNECTION_ID))
        .thenReturn(new StandardSourceDefinition()
            .withReleaseStage(SOURCE_RELEASE_STAGE)
            .withSourceDefinitionId(SOURCE_DEFINITION_ID)
            .withName(SOURCE_DEFINITION_NAME));

    Mockito.doThrow(new RuntimeException("some exception"))
        .when(jobErrorReportingClient)
        .reportJobFailureReason(Mockito.any(), Mockito.eq(sourceFailureReason), Mockito.any(), Mockito.any());

    Assertions.assertDoesNotThrow(() -> jobErrorReporter.reportSyncJobFailure(CONNECTION_ID, mFailureSummary, mJobSyncConfig));
    Mockito.verify(jobErrorReportingClient, Mockito.times(1))
        .reportJobFailureReason(Mockito.any(), Mockito.any(), Mockito.any(), Mockito.any());
  }

}
