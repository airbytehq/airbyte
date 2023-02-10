/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.scheduling.activities;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.api.client.generated.AttemptApi;
import io.airbyte.api.client.generated.StateApi;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.ConnectionState;
import io.airbyte.api.client.model.generated.ConnectionStateType;
import io.airbyte.api.client.model.generated.SaveAttemptSyncConfigRequestBody;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.server.converters.ApiPojoConverters;
import io.airbyte.config.AttemptSyncConfig;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncInput;
import io.airbyte.config.State;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.persistence.job.JobPersistence;
import io.airbyte.persistence.job.factory.OAuthConfigSupplier;
import io.airbyte.persistence.job.models.IntegrationLauncherConfig;
import io.airbyte.persistence.job.models.Job;
import io.airbyte.persistence.job.models.JobRunConfig;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.validation.json.JsonValidationException;
import io.airbyte.workers.WorkerConstants;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.GeneratedJobInput;
import io.airbyte.workers.temporal.scheduling.activities.GenerateInputActivity.SyncInput;
import java.io.IOException;
import java.util.Map;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
class GenerateInputActivityTest {

  static private AttemptApi attemptApi;
  static private JobPersistence jobPersistence;
  static private ConfigRepository configRepository;
  static private GenerateInputActivityImpl generateInputActivity;
  static private OAuthConfigSupplier oAuthConfigSupplier;
  static private Job job;

  static private final JsonNode SOURCE_CONFIGURATION = Jsons.jsonNode(Map.of("source_key", "source_value"));
  static private final JsonNode SOURCE_CONFIG_WITH_OAUTH = Jsons.jsonNode(Map.of("source_key", "source_value", "oauth", "oauth_value"));
  static private final JsonNode DESTINATION_CONFIGURATION = Jsons.jsonNode(Map.of("destination_key", "destination_value"));
  static private final JsonNode DESTINATION_CONFIG_WITH_OAUTH =
      Jsons.jsonNode(Map.of("destination_key", "destination_value", "oauth", "oauth_value"));
  static private final State STATE = new State().withState(Jsons.jsonNode(Map.of("state_key", "state_value")));

  static private final UUID WORKSPACE_ID = UUID.randomUUID();
  static private final long JOB_ID = 1;
  static private final int ATTEMPT_ID = 1;
  static private final UUID SOURCE_ID = UUID.randomUUID();
  static private final UUID DESTINATION_DEFINITION_ID = UUID.randomUUID();
  static private final UUID DESTINATION_ID = UUID.randomUUID();
  static private final UUID CONNECTION_ID = UUID.randomUUID();

  @BeforeEach
  void setUp() throws IOException, JsonValidationException, ConfigNotFoundException, ApiException {
    final StateApi stateApi = mock(StateApi.class);
    final FeatureFlags featureFlags = mock(FeatureFlags.class);

    oAuthConfigSupplier = mock(OAuthConfigSupplier.class);
    attemptApi = mock(AttemptApi.class);
    jobPersistence = mock(JobPersistence.class);
    configRepository = mock(ConfigRepository.class);
    generateInputActivity = new GenerateInputActivityImpl(jobPersistence, configRepository, stateApi, attemptApi, featureFlags, oAuthConfigSupplier);

    job = mock(Job.class);

    when(jobPersistence.getJob(JOB_ID)).thenReturn(job);

    final DestinationConnection destinationConnection = new DestinationConnection()
        .withDestinationId(DESTINATION_ID)
        .withWorkspaceId(WORKSPACE_ID)
        .withDestinationDefinitionId(DESTINATION_DEFINITION_ID)
        .withConfiguration(DESTINATION_CONFIGURATION);
    when(configRepository.getDestinationConnection(DESTINATION_ID)).thenReturn(destinationConnection);
    when(configRepository.getStandardDestinationDefinition(DESTINATION_DEFINITION_ID)).thenReturn(mock(StandardDestinationDefinition.class));
    when(configRepository.getSourceDefinitionFromSource(SOURCE_ID)).thenReturn(mock(StandardSourceDefinition.class));
    when(oAuthConfigSupplier.injectDestinationOAuthParameters(DESTINATION_DEFINITION_ID, WORKSPACE_ID, DESTINATION_CONFIGURATION))
        .thenReturn(DESTINATION_CONFIG_WITH_OAUTH);

    final StandardSync standardSync = new StandardSync()
        .withSourceId(SOURCE_ID)
        .withDestinationId(DESTINATION_ID);
    when(configRepository.getStandardSync(CONNECTION_ID)).thenReturn(standardSync);

    when(stateApi.getState(new ConnectionIdRequestBody().connectionId(CONNECTION_ID)))
        .thenReturn(new ConnectionState()
            .stateType(ConnectionStateType.LEGACY)
            .state(STATE.getState()));
  }

  @Test
  void testGetSyncWorkflowInput() throws JsonValidationException, ConfigNotFoundException, IOException, ApiException {
    final SyncInput syncInput = new SyncInput(ATTEMPT_ID, JOB_ID);

    final UUID sourceDefinitionId = UUID.randomUUID();
    final SourceConnection sourceConnection = new SourceConnection()
        .withSourceId(SOURCE_ID)
        .withSourceDefinitionId(sourceDefinitionId)
        .withWorkspaceId(WORKSPACE_ID)
        .withConfiguration(SOURCE_CONFIGURATION);
    when(configRepository.getSourceConnection(SOURCE_ID)).thenReturn(sourceConnection);
    when(oAuthConfigSupplier.injectSourceOAuthParameters(sourceDefinitionId, WORKSPACE_ID, SOURCE_CONFIGURATION))
        .thenReturn(SOURCE_CONFIG_WITH_OAUTH);

    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withWorkspaceId(UUID.randomUUID())
        .withDestinationDockerImage("destinationDockerImage")
        .withSourceDockerImage("sourceDockerImage")
        .withConfiguredAirbyteCatalog(mock(ConfiguredAirbyteCatalog.class));

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.SYNC)
        .withSync(jobSyncConfig);

    when(job.getConfig()).thenReturn(jobConfig);
    when(job.getScope()).thenReturn(CONNECTION_ID.toString());

    final StandardSyncInput expectedStandardSyncInput = new StandardSyncInput()
        .withWorkspaceId(jobSyncConfig.getWorkspaceId())
        .withSourceId(SOURCE_ID)
        .withDestinationId(DESTINATION_ID)
        .withSourceConfiguration(SOURCE_CONFIG_WITH_OAUTH)
        .withDestinationConfiguration(DESTINATION_CONFIG_WITH_OAUTH)
        .withState(STATE)
        .withCatalog(jobSyncConfig.getConfiguredAirbyteCatalog())
        .withWorkspaceId(jobSyncConfig.getWorkspaceId());

    final JobRunConfig expectedJobRunConfig = new JobRunConfig()
        .withJobId(String.valueOf(JOB_ID))
        .withAttemptId((long) ATTEMPT_ID);

    final IntegrationLauncherConfig expectedSourceLauncherConfig = new IntegrationLauncherConfig()
        .withJobId(String.valueOf(JOB_ID))
        .withAttemptId((long) ATTEMPT_ID)
        .withDockerImage(jobSyncConfig.getSourceDockerImage());

    final IntegrationLauncherConfig expectedDestinationLauncherConfig = new IntegrationLauncherConfig()
        .withJobId(String.valueOf(JOB_ID))
        .withAttemptId((long) ATTEMPT_ID)
        .withDockerImage(jobSyncConfig.getDestinationDockerImage());

    final GeneratedJobInput expectedGeneratedJobInput = new GeneratedJobInput(
        expectedJobRunConfig,
        expectedSourceLauncherConfig,
        expectedDestinationLauncherConfig,
        expectedStandardSyncInput);

    final GeneratedJobInput generatedJobInput = generateInputActivity.getSyncWorkflowInput(syncInput);
    assertEquals(expectedGeneratedJobInput, generatedJobInput);

    final AttemptSyncConfig expectedAttemptSyncConfig = new AttemptSyncConfig()
        .withSourceConfiguration(SOURCE_CONFIG_WITH_OAUTH)
        .withDestinationConfiguration(DESTINATION_CONFIG_WITH_OAUTH)
        .withState(STATE);

    verify(oAuthConfigSupplier).injectSourceOAuthParameters(sourceDefinitionId, WORKSPACE_ID, SOURCE_CONFIGURATION);
    verify(oAuthConfigSupplier).injectDestinationOAuthParameters(DESTINATION_DEFINITION_ID, WORKSPACE_ID, DESTINATION_CONFIGURATION);

    verify(attemptApi).saveSyncConfig(new SaveAttemptSyncConfigRequestBody()
        .jobId(JOB_ID)
        .attemptNumber(ATTEMPT_ID)
        .syncConfig(ApiPojoConverters.attemptSyncConfigToClient(expectedAttemptSyncConfig, CONNECTION_ID, true)));
  }

  @Test
  void testGetResetSyncWorkflowInput() throws IOException, ApiException {
    final SyncInput syncInput = new SyncInput(ATTEMPT_ID, JOB_ID);

    final JobResetConnectionConfig jobResetConfig = new JobResetConnectionConfig()
        .withWorkspaceId(UUID.randomUUID())
        .withDestinationDockerImage("destinationDockerImage")
        .withConfiguredAirbyteCatalog(mock(ConfiguredAirbyteCatalog.class));

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.RESET_CONNECTION)
        .withResetConnection(jobResetConfig);

    when(job.getConfig()).thenReturn(jobConfig);
    when(job.getScope()).thenReturn(CONNECTION_ID.toString());

    final StandardSyncInput expectedStandardSyncInput = new StandardSyncInput()
        .withWorkspaceId(jobResetConfig.getWorkspaceId())
        .withSourceId(SOURCE_ID)
        .withDestinationId(DESTINATION_ID)
        .withSourceConfiguration(Jsons.emptyObject())
        .withDestinationConfiguration(DESTINATION_CONFIG_WITH_OAUTH)
        .withState(STATE)
        .withCatalog(jobResetConfig.getConfiguredAirbyteCatalog())
        .withWorkspaceId(jobResetConfig.getWorkspaceId());

    final JobRunConfig expectedJobRunConfig = new JobRunConfig()
        .withJobId(String.valueOf(JOB_ID))
        .withAttemptId((long) ATTEMPT_ID);

    final IntegrationLauncherConfig expectedSourceLauncherConfig = new IntegrationLauncherConfig()
        .withJobId(String.valueOf(JOB_ID))
        .withAttemptId((long) ATTEMPT_ID)
        .withDockerImage(WorkerConstants.RESET_JOB_SOURCE_DOCKER_IMAGE_STUB);

    final IntegrationLauncherConfig expectedDestinationLauncherConfig = new IntegrationLauncherConfig()
        .withJobId(String.valueOf(JOB_ID))
        .withAttemptId((long) ATTEMPT_ID)
        .withDockerImage(jobResetConfig.getDestinationDockerImage());

    final GeneratedJobInput expectedGeneratedJobInput = new GeneratedJobInput(
        expectedJobRunConfig,
        expectedSourceLauncherConfig,
        expectedDestinationLauncherConfig,
        expectedStandardSyncInput);

    final GeneratedJobInput generatedJobInput = generateInputActivity.getSyncWorkflowInput(syncInput);
    assertEquals(expectedGeneratedJobInput, generatedJobInput);

    final AttemptSyncConfig expectedAttemptSyncConfig = new AttemptSyncConfig()
        .withSourceConfiguration(Jsons.emptyObject())
        .withDestinationConfiguration(DESTINATION_CONFIG_WITH_OAUTH)
        .withState(STATE);

    verify(oAuthConfigSupplier).injectDestinationOAuthParameters(DESTINATION_DEFINITION_ID, WORKSPACE_ID, DESTINATION_CONFIGURATION);

    verify(attemptApi).saveSyncConfig(new SaveAttemptSyncConfigRequestBody()
        .jobId(JOB_ID)
        .attemptNumber(ATTEMPT_ID)
        .syncConfig(ApiPojoConverters.attemptSyncConfigToClient(expectedAttemptSyncConfig, CONNECTION_ID, true)));
  }

}
