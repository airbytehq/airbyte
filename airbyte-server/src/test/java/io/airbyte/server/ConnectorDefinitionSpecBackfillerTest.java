/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server;

import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyMap;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import io.airbyte.analytics.TrackingClient;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ConfigSchema;
import io.airbyte.config.Configs;
import io.airbyte.config.Configs.WorkerEnvironment;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardDestinationDefinition;
import io.airbyte.config.StandardSourceDefinition;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardWorkspace;
import io.airbyte.config.helpers.LogConfigs;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.config.persistence.ConfigPersistence;
import io.airbyte.config.persistence.ConfigRepository;
import io.airbyte.protocol.models.ConnectorSpecification;
import io.airbyte.scheduler.client.SynchronousJobMetadata;
import io.airbyte.scheduler.client.SynchronousResponse;
import io.airbyte.scheduler.client.SynchronousSchedulerClient;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import java.net.URI;
import java.nio.file.Path;
import java.time.Instant;
import java.util.List;
import java.util.Set;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class ConnectorDefinitionSpecBackfillerTest {

  private static final String SOURCE_DEF_NAME = "source-definition";
  private static final String DEST_DEF_NAME = "destination-definition";
  private static final String SOURCE_DOCKER_REPO = "docker-repo/source";
  private static final String DEST_DOCKER_REPO = "docker-repo/destination";
  private static final String DOCKER_IMAGE_TAG = "tag";
  private static final String FAILED_SPEC_BACKFILL_ACTION = "failed_spec_backfill";
  private static final StandardWorkspace WORKSPACE = new StandardWorkspace().withWorkspaceId(UUID.randomUUID());

  private ConfigRepository configRepository;
  private ConfigPersistence database;
  private ConfigPersistence seed;
  private TrackingClient trackingClient;
  private SynchronousSchedulerClient schedulerClient;
  private Configs configs;

  @BeforeEach
  void setup() throws IOException, JsonValidationException {
    configRepository = mock(ConfigRepository.class);
    when(configRepository.listStandardWorkspaces(true)).thenReturn(List.of(WORKSPACE));

    database = mock(ConfigPersistence.class);
    seed = mock(ConfigPersistence.class);
    trackingClient = mock(TrackingClient.class);
    schedulerClient = mock(SynchronousSchedulerClient.class);
    configs = mock(Configs.class);
    when(configs.getWorkerEnvironment()).thenReturn(WorkerEnvironment.DOCKER);
    when(configs.getLogConfigs()).thenReturn(mock(LogConfigs.class));
  }

  @Test
  public void testBackfillSpecSuccessful() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardSourceDefinition sourceDef = new StandardSourceDefinition().withSourceDefinitionId(UUID.randomUUID())
        .withDockerRepository(SOURCE_DOCKER_REPO)
        .withDockerImageTag(DOCKER_IMAGE_TAG)
        .withName(SOURCE_DEF_NAME);
    final StandardDestinationDefinition destDef = new StandardDestinationDefinition().withDestinationDefinitionId(UUID.randomUUID())
        .withDockerRepository(DEST_DOCKER_REPO)
        .withDockerImageTag(DOCKER_IMAGE_TAG)
        .withName(DEST_DEF_NAME);

    when(configRepository.listStandardSourceDefinitions()).thenReturn(List.of(sourceDef));
    when(configRepository.listStandardDestinationDefinitions()).thenReturn(List.of(destDef));
    // source def is in use but not in seed, should be backfilled
    when(configRepository.getConnectorReposInUse()).thenReturn(Set.of(SOURCE_DOCKER_REPO));
    when(seed.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class)).thenReturn(List.of());
    // dest def is not in use but is in seed, should be backfilled
    when(seed.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class)).thenReturn(List.of(destDef));

    final ConnectorSpecification sourceSpec = new ConnectorSpecification().withDocumentationUrl(URI.create("http://source.org"));
    final ConnectorSpecification destSpec = new ConnectorSpecification().withDocumentationUrl(URI.create("http://dest.org"));

    final SynchronousResponse<ConnectorSpecification> successfulSourceResponse = new SynchronousResponse<>(
        sourceSpec,
        mockJobMetadata(true));
    final SynchronousResponse<ConnectorSpecification> successfulDestResponse = new SynchronousResponse<>(
        destSpec,
        mockJobMetadata(true));

    final SynchronousSchedulerClient schedulerClient = mock(SynchronousSchedulerClient.class);
    when(schedulerClient.createGetSpecJob(SOURCE_DOCKER_REPO + ":" + DOCKER_IMAGE_TAG)).thenReturn(successfulSourceResponse);
    when(schedulerClient.createGetSpecJob(DEST_DOCKER_REPO + ":" + DOCKER_IMAGE_TAG)).thenReturn(successfulDestResponse);

    ConnectorDefinitionSpecBackfiller.migrateAllDefinitionsToContainSpec(
        configRepository,
        database,
        seed,
        schedulerClient,
        trackingClient,
        configs);

    final StandardSourceDefinition expectedSourceDef = Jsons.clone(sourceDef).withSpec(sourceSpec);
    final StandardDestinationDefinition expectedDestDef = Jsons.clone(destDef).withSpec(destSpec);
    verify(configRepository, times(1)).writeStandardSourceDefinition(expectedSourceDef);
    verify(configRepository, times(1)).writeStandardDestinationDefinition(expectedDestDef);
    verify(database, never()).deleteConfig(any(), any());
  }

  @Test
  public void testDeleteUnusedDefinitionsNotInSeed() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardSourceDefinition sourceDef = new StandardSourceDefinition().withSourceDefinitionId(UUID.randomUUID())
        .withDockerRepository(SOURCE_DOCKER_REPO)
        .withDockerImageTag(DOCKER_IMAGE_TAG)
        .withName(SOURCE_DEF_NAME);
    final StandardDestinationDefinition destDef = new StandardDestinationDefinition().withDestinationDefinitionId(UUID.randomUUID())
        .withDockerRepository(DEST_DOCKER_REPO)
        .withDockerImageTag(DOCKER_IMAGE_TAG)
        .withName(DEST_DEF_NAME);

    when(configRepository.listStandardSourceDefinitions()).thenReturn(List.of(sourceDef));
    when(configRepository.listStandardDestinationDefinitions()).thenReturn(List.of(destDef));
    // both source and destination definitions are not in use and are not in the seed, should be deleted
    when(configRepository.getConnectorReposInUse()).thenReturn(Set.of());
    when(seed.listConfigs(ConfigSchema.STANDARD_SOURCE_DEFINITION, StandardSourceDefinition.class)).thenReturn(List.of());
    when(seed.listConfigs(ConfigSchema.STANDARD_DESTINATION_DEFINITION, StandardDestinationDefinition.class)).thenReturn(List.of());

    when(database.listConfigs(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class)).thenReturn(List.of());
    when(database.listConfigs(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class)).thenReturn(List.of());

    ConnectorDefinitionSpecBackfiller.migrateAllDefinitionsToContainSpec(
        configRepository,
        database,
        seed,
        schedulerClient,
        trackingClient,
        configs);

    verify(configRepository, never()).writeStandardSourceDefinition(any());
    verify(configRepository, never()).writeStandardDestinationDefinition(any());
    verify(database, times(1)).deleteConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, sourceDef.getSourceDefinitionId().toString());
    verify(database, times(1)).deleteConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destDef.getDestinationDefinitionId().toString());
  }

  @Test
  public void testBackfillSpecFailureNonForceUpgrade() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardSourceDefinition sourceDef = new StandardSourceDefinition().withSourceDefinitionId(UUID.randomUUID())
        .withDockerRepository(SOURCE_DOCKER_REPO)
        .withDockerImageTag(DOCKER_IMAGE_TAG)
        .withName(SOURCE_DEF_NAME);
    final StandardDestinationDefinition destDef = new StandardDestinationDefinition().withDestinationDefinitionId(UUID.randomUUID())
        .withDockerRepository(DEST_DOCKER_REPO)
        .withDockerImageTag(DOCKER_IMAGE_TAG)
        .withName(DEST_DEF_NAME);

    when(configRepository.listStandardSourceDefinitions()).thenReturn(List.of(sourceDef));
    when(configRepository.listStandardDestinationDefinitions()).thenReturn(List.of(destDef));
    // both source and destination definitions are in use, so should be backfilled
    when(configRepository.getConnectorReposInUse()).thenReturn(Set.of(SOURCE_DOCKER_REPO, DEST_DOCKER_REPO));

    final SynchronousResponse<ConnectorSpecification> failureSourceResponse = new SynchronousResponse<>(
        null,
        mockJobMetadata(false));
    final SynchronousResponse<ConnectorSpecification> failureDestResponse = new SynchronousResponse<>(
        null,
        mockJobMetadata(false));

    when(schedulerClient.createGetSpecJob(SOURCE_DOCKER_REPO + ":" + DOCKER_IMAGE_TAG)).thenReturn(failureSourceResponse);
    when(schedulerClient.createGetSpecJob(DEST_DOCKER_REPO + ":" + DOCKER_IMAGE_TAG)).thenReturn(failureDestResponse);

    // do not force upgrade, should fail with an error instead
    when(configs.getVersion31ForceUpgrade()).thenReturn(false);

    assertThatThrownBy(() -> ConnectorDefinitionSpecBackfiller.migrateAllDefinitionsToContainSpec(
        configRepository,
        database,
        seed,
        schedulerClient,
        trackingClient,
        configs))
        .isInstanceOf(RuntimeException.class)
        .hasMessageContaining(
            "Specs could not be retrieved for the following connector images: ["
                + SOURCE_DOCKER_REPO + ":" + DOCKER_IMAGE_TAG + ", " + DEST_DOCKER_REPO + ":" + DOCKER_IMAGE_TAG + "]");

    verify(configRepository, never()).writeStandardSourceDefinition(any());
    verify(configRepository, never()).writeStandardDestinationDefinition(any());
    verify(database, never()).deleteConfig(any(), any());

    verify(trackingClient, times(2)).track(eq(WORKSPACE.getWorkspaceId()), eq(FAILED_SPEC_BACKFILL_ACTION), anyMap());
  }

  @Test
  public void testBackfillSpecFailureForceUpgrade() throws JsonValidationException, IOException, ConfigNotFoundException {
    final StandardSourceDefinition sourceDef = new StandardSourceDefinition().withSourceDefinitionId(UUID.randomUUID())
        .withDockerRepository(SOURCE_DOCKER_REPO)
        .withDockerImageTag(DOCKER_IMAGE_TAG)
        .withName(SOURCE_DEF_NAME);
    final StandardDestinationDefinition destDef = new StandardDestinationDefinition().withDestinationDefinitionId(UUID.randomUUID())
        .withDockerRepository(DEST_DOCKER_REPO)
        .withDockerImageTag(DOCKER_IMAGE_TAG)
        .withName(DEST_DEF_NAME);

    when(configRepository.listStandardSourceDefinitions()).thenReturn(List.of(sourceDef));
    when(configRepository.listStandardDestinationDefinitions()).thenReturn(List.of(destDef));
    // both source and destination definitions are in use, so should be backfilled
    when(configRepository.getConnectorReposInUse()).thenReturn(Set.of(SOURCE_DOCKER_REPO, DEST_DOCKER_REPO));

    final SourceConnection sourceConnection = new SourceConnection().withSourceId(UUID.randomUUID())
        .withSourceDefinitionId(sourceDef.getSourceDefinitionId());
    when(database.listConfigs(ConfigSchema.SOURCE_CONNECTION, SourceConnection.class)).thenReturn(List.of(sourceConnection));
    final DestinationConnection destConnection = new DestinationConnection().withDestinationId(UUID.randomUUID())
        .withDestinationDefinitionId(destDef.getDestinationDefinitionId());
    when(database.listConfigs(ConfigSchema.DESTINATION_CONNECTION, DestinationConnection.class)).thenReturn(List.of(destConnection));

    final StandardSync sourceSync = new StandardSync().withConnectionId(UUID.randomUUID()).withSourceId(sourceConnection.getSourceId())
        .withDestinationId(UUID.randomUUID());
    final StandardSync destSync = new StandardSync().withConnectionId(UUID.randomUUID()).withDestinationId(destConnection.getDestinationId())
        .withSourceId(UUID.randomUUID());
    when(database.listConfigs(ConfigSchema.STANDARD_SYNC, StandardSync.class)).thenReturn(List.of(sourceSync, destSync));

    final SynchronousResponse<ConnectorSpecification> failureSourceResponse = new SynchronousResponse<>(
        null,
        mockJobMetadata(false));
    final SynchronousResponse<ConnectorSpecification> failureDestResponse = new SynchronousResponse<>(
        null,
        mockJobMetadata(false));

    when(schedulerClient.createGetSpecJob(SOURCE_DOCKER_REPO + ":" + DOCKER_IMAGE_TAG)).thenReturn(failureSourceResponse);
    when(schedulerClient.createGetSpecJob(DEST_DOCKER_REPO + ":" + DOCKER_IMAGE_TAG)).thenReturn(failureDestResponse);

    // force upgrade, specs should be deleted
    when(configs.getVersion31ForceUpgrade()).thenReturn(true);

    ConnectorDefinitionSpecBackfiller.migrateAllDefinitionsToContainSpec(
        configRepository,
        database,
        seed,
        schedulerClient,
        trackingClient,
        configs);

    verify(configRepository, never()).writeStandardSourceDefinition(any());
    verify(configRepository, never()).writeStandardDestinationDefinition(any());

    verify(trackingClient, times(2)).track(eq(WORKSPACE.getWorkspaceId()), eq(FAILED_SPEC_BACKFILL_ACTION), anyMap());

    verify(database, times(1)).deleteConfig(ConfigSchema.STANDARD_SYNC, sourceSync.getConnectionId().toString());
    verify(database, times(1)).deleteConfig(ConfigSchema.STANDARD_SYNC, destSync.getConnectionId().toString());
    verify(database, times(1)).deleteConfig(ConfigSchema.SOURCE_CONNECTION, sourceConnection.getSourceId().toString());
    verify(database, times(1)).deleteConfig(ConfigSchema.DESTINATION_CONNECTION, destConnection.getDestinationId().toString());
    verify(database, times(1)).deleteConfig(ConfigSchema.STANDARD_SOURCE_DEFINITION, sourceDef.getSourceDefinitionId().toString());
    verify(database, times(1)).deleteConfig(ConfigSchema.STANDARD_DESTINATION_DEFINITION, destDef.getDestinationDefinitionId().toString());
  }

  @Test
  public void testSpecAlreadyExists() throws JsonValidationException, IOException, ConfigNotFoundException {
    final ConnectorSpecification sourceSpec = new ConnectorSpecification().withDocumentationUrl(URI.create("http://source.org"));
    final ConnectorSpecification destSpec = new ConnectorSpecification().withDocumentationUrl(URI.create("http://dest.org"));
    final StandardSourceDefinition sourceDef = new StandardSourceDefinition().withDockerRepository(SOURCE_DOCKER_REPO)
        .withDockerImageTag(DOCKER_IMAGE_TAG).withSpec(sourceSpec);
    final StandardDestinationDefinition destDef = new StandardDestinationDefinition().withDockerRepository(DEST_DOCKER_REPO)
        .withDockerImageTag(DOCKER_IMAGE_TAG).withSpec(destSpec);

    when(configRepository.listStandardSourceDefinitions()).thenReturn(List.of(sourceDef));
    when(configRepository.listStandardDestinationDefinitions()).thenReturn(List.of(destDef));

    ConnectorDefinitionSpecBackfiller.migrateAllDefinitionsToContainSpec(
        configRepository,
        database,
        seed,
        schedulerClient,
        trackingClient,
        configs);

    verify(schedulerClient, never()).createGetSpecJob(any());
    verify(configRepository, never()).writeStandardSourceDefinition(any());
    verify(configRepository, never()).writeStandardDestinationDefinition(any());
    verify(database, never()).deleteConfig(any(), any());
  }

  private SynchronousJobMetadata mockJobMetadata(final boolean succeeded) {
    final long now = Instant.now().toEpochMilli();
    return new SynchronousJobMetadata(
        UUID.randomUUID(),
        ConfigType.GET_SPEC,
        UUID.randomUUID(),
        now,
        now,
        succeeded,
        Path.of("path", "to", "logs"));
  }

}
