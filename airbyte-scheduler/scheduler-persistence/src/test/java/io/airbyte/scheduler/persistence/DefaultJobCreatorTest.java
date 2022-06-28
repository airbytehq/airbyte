/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.scheduler.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ActorDefinitionResourceRequirements;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.JobTypeResourceLimit;
import io.airbyte.config.JobTypeResourceLimit.JobType;
import io.airbyte.config.OperatorNormalization;
import io.airbyte.config.OperatorNormalization.Option;
import io.airbyte.config.ResetSourceConfiguration;
import io.airbyte.config.ResourceRequirements;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import io.airbyte.config.State;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.protocol.models.SyncMode;
import java.io.IOException;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class DefaultJobCreatorTest {

  private static final String STREAM1_NAME = "stream1";
  private static final String STREAM2_NAME = "stream2";
  private static final String STREAM3_NAME = "stream3";
  private static final String NAMESPACE = "namespace";
  private static final String FIELD_NAME = "id";
  private static final StreamDescriptor STREAM1_DESCRIPTOR = new StreamDescriptor().withName(STREAM1_NAME);
  private static final StreamDescriptor STREAM2_DESCRIPTOR = new StreamDescriptor().withName(STREAM2_NAME).withNamespace(NAMESPACE);

  private static final String SOURCE_IMAGE_NAME = "daxtarity/sourceimagename";
  private static final String DESTINATION_IMAGE_NAME = "daxtarity/destinationimagename";
  private static final SourceConnection SOURCE_CONNECTION;
  private static final DestinationConnection DESTINATION_CONNECTION;
  private static final StandardSync STANDARD_SYNC;
  private static final StandardSyncOperation STANDARD_SYNC_OPERATION;
  private static final long JOB_ID = 12L;

  private JobPersistence jobPersistence;
  private StatePersistence statePersistence;
  private JobCreator jobCreator;
  private ResourceRequirements workerResourceRequirements;

  static {
    final UUID workspaceId = UUID.randomUUID();
    final UUID sourceId = UUID.randomUUID();
    final UUID sourceDefinitionId = UUID.randomUUID();

    final JsonNode implementationJson = Jsons.jsonNode(ImmutableMap.builder()
        .put("apiKey", "123-abc")
        .put("hostname", "airbyte.io")
        .build());

    SOURCE_CONNECTION = new SourceConnection()
        .withWorkspaceId(workspaceId)
        .withSourceDefinitionId(sourceDefinitionId)
        .withSourceId(sourceId)
        .withConfiguration(implementationJson)
        .withTombstone(false);

    final UUID destinationId = UUID.randomUUID();
    final UUID destinationDefinitionId = UUID.randomUUID();

    DESTINATION_CONNECTION = new DestinationConnection()
        .withWorkspaceId(workspaceId)
        .withDestinationDefinitionId(destinationDefinitionId)
        .withDestinationId(destinationId)
        .withConfiguration(implementationJson)
        .withTombstone(false);

    final UUID connectionId = UUID.randomUUID();
    final UUID operationId = UUID.randomUUID();

    final ConfiguredAirbyteStream stream1 = new ConfiguredAirbyteStream()
        .withStream(CatalogHelpers.createAirbyteStream(STREAM1_NAME, Field.of(FIELD_NAME, JsonSchemaType.STRING)));
    final ConfiguredAirbyteStream stream2 = new ConfiguredAirbyteStream()
        .withStream(CatalogHelpers.createAirbyteStream(STREAM2_NAME, NAMESPACE, Field.of(FIELD_NAME, JsonSchemaType.STRING)));
    final ConfiguredAirbyteStream stream3 = new ConfiguredAirbyteStream()
        .withStream(CatalogHelpers.createAirbyteStream(STREAM3_NAME, NAMESPACE, Field.of(FIELD_NAME, JsonSchemaType.STRING)));
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(stream1, stream2, stream3));

    STANDARD_SYNC = new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi")
        .withNamespaceDefinition(NamespaceDefinitionType.SOURCE)
        .withNamespaceFormat(null)
        .withPrefix("presto_to_hudi")
        .withStatus(StandardSync.Status.ACTIVE)
        .withCatalog(catalog)
        .withSourceId(sourceId)
        .withDestinationId(destinationId)
        .withOperationIds(List.of(operationId));

    STANDARD_SYNC_OPERATION = new StandardSyncOperation()
        .withOperationId(operationId)
        .withName("normalize")
        .withTombstone(false)
        .withOperatorType(OperatorType.NORMALIZATION)
        .withOperatorNormalization(new OperatorNormalization().withOption(Option.BASIC));
  }

  @BeforeEach
  void setup() {
    jobPersistence = mock(JobPersistence.class);
    statePersistence = mock(StatePersistence.class);
    workerResourceRequirements = new ResourceRequirements()
        .withCpuLimit("0.2")
        .withCpuRequest("0.2")
        .withMemoryLimit("200Mi")
        .withMemoryRequest("200Mi");
    jobCreator = new DefaultJobCreator(jobPersistence, workerResourceRequirements, statePersistence);
  }

  @Test
  void testCreateSyncJob() throws IOException {
    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withNamespaceDefinition(STANDARD_SYNC.getNamespaceDefinition())
        .withNamespaceFormat(STANDARD_SYNC.getNamespaceFormat())
        .withPrefix(STANDARD_SYNC.getPrefix())
        .withSourceConfiguration(SOURCE_CONNECTION.getConfiguration())
        .withSourceDockerImage(SOURCE_IMAGE_NAME)
        .withDestinationConfiguration(DESTINATION_CONNECTION.getConfiguration())
        .withDestinationDockerImage(DESTINATION_IMAGE_NAME)
        .withConfiguredAirbyteCatalog(STANDARD_SYNC.getCatalog())
        .withOperationSequence(List.of(STANDARD_SYNC_OPERATION))
        .withResourceRequirements(workerResourceRequirements)
        .withSourceResourceRequirements(workerResourceRequirements)
        .withDestinationResourceRequirements(workerResourceRequirements);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.SYNC)
        .withSync(jobSyncConfig);

    final String expectedScope = STANDARD_SYNC.getConnectionId().toString();
    when(jobPersistence.enqueueJob(expectedScope, jobConfig)).thenReturn(Optional.of(JOB_ID));

    final long jobId = jobCreator.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME,
        List.of(STANDARD_SYNC_OPERATION),
        null,
        null).orElseThrow();
    assertEquals(JOB_ID, jobId);
  }

  @Test
  void testCreateSyncJobEnsureNoQueuing() throws IOException {
    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withNamespaceDefinition(STANDARD_SYNC.getNamespaceDefinition())
        .withNamespaceFormat(STANDARD_SYNC.getNamespaceFormat())
        .withPrefix(STANDARD_SYNC.getPrefix())
        .withSourceConfiguration(SOURCE_CONNECTION.getConfiguration())
        .withSourceDockerImage(SOURCE_IMAGE_NAME)
        .withDestinationConfiguration(DESTINATION_CONNECTION.getConfiguration())
        .withDestinationDockerImage(DESTINATION_IMAGE_NAME)
        .withConfiguredAirbyteCatalog(STANDARD_SYNC.getCatalog())
        .withOperationSequence(List.of(STANDARD_SYNC_OPERATION))
        .withResourceRequirements(workerResourceRequirements);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.SYNC)
        .withSync(jobSyncConfig);

    final String expectedScope = STANDARD_SYNC.getConnectionId().toString();
    when(jobPersistence.enqueueJob(expectedScope, jobConfig)).thenReturn(Optional.empty());

    assertTrue(jobCreator.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME,
        List.of(STANDARD_SYNC_OPERATION),
        null,
        null).isEmpty());
  }

  @Test
  void testCreateSyncJobDefaultWorkerResourceReqs() throws IOException {
    jobCreator.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME,
        List.of(STANDARD_SYNC_OPERATION),
        null,
        null);

    final JobSyncConfig expectedJobSyncConfig = new JobSyncConfig()
        .withNamespaceDefinition(STANDARD_SYNC.getNamespaceDefinition())
        .withNamespaceFormat(STANDARD_SYNC.getNamespaceFormat())
        .withPrefix(STANDARD_SYNC.getPrefix())
        .withSourceConfiguration(SOURCE_CONNECTION.getConfiguration())
        .withSourceDockerImage(SOURCE_IMAGE_NAME)
        .withDestinationConfiguration(DESTINATION_CONNECTION.getConfiguration())
        .withDestinationDockerImage(DESTINATION_IMAGE_NAME)
        .withConfiguredAirbyteCatalog(STANDARD_SYNC.getCatalog())
        .withOperationSequence(List.of(STANDARD_SYNC_OPERATION))
        .withResourceRequirements(workerResourceRequirements)
        .withSourceResourceRequirements(workerResourceRequirements)
        .withDestinationResourceRequirements(workerResourceRequirements);

    final JobConfig expectedJobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.SYNC)
        .withSync(expectedJobSyncConfig);

    final String expectedScope = STANDARD_SYNC.getConnectionId().toString();

    verify(jobPersistence, times(1)).enqueueJob(expectedScope, expectedJobConfig);
  }

  @Test
  void testCreateSyncJobConnectionResourceReqs() throws IOException {
    final ResourceRequirements standardSyncResourceRequirements = new ResourceRequirements()
        .withCpuLimit("0.5")
        .withCpuRequest("0.5")
        .withMemoryLimit("500Mi")
        .withMemoryRequest("500Mi");
    final StandardSync standardSync = Jsons.clone(STANDARD_SYNC).withResourceRequirements(standardSyncResourceRequirements);

    jobCreator.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        standardSync,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME,
        List.of(STANDARD_SYNC_OPERATION),
        null,
        null);

    final JobSyncConfig expectedJobSyncConfig = new JobSyncConfig()
        .withNamespaceDefinition(STANDARD_SYNC.getNamespaceDefinition())
        .withNamespaceFormat(STANDARD_SYNC.getNamespaceFormat())
        .withPrefix(STANDARD_SYNC.getPrefix())
        .withSourceConfiguration(SOURCE_CONNECTION.getConfiguration())
        .withSourceDockerImage(SOURCE_IMAGE_NAME)
        .withDestinationConfiguration(DESTINATION_CONNECTION.getConfiguration())
        .withDestinationDockerImage(DESTINATION_IMAGE_NAME)
        .withConfiguredAirbyteCatalog(STANDARD_SYNC.getCatalog())
        .withOperationSequence(List.of(STANDARD_SYNC_OPERATION))
        .withResourceRequirements(standardSyncResourceRequirements)
        .withSourceResourceRequirements(standardSyncResourceRequirements)
        .withDestinationResourceRequirements(standardSyncResourceRequirements);

    final JobConfig expectedJobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.SYNC)
        .withSync(expectedJobSyncConfig);

    final String expectedScope = STANDARD_SYNC.getConnectionId().toString();

    verify(jobPersistence, times(1)).enqueueJob(expectedScope, expectedJobConfig);
  }

  @Test
  void testCreateSyncJobSourceAndDestinationResourceReqs() throws IOException {
    final ResourceRequirements sourceResourceRequirements = new ResourceRequirements()
        .withCpuLimit("0.7")
        .withCpuRequest("0.7")
        .withMemoryLimit("700Mi")
        .withMemoryRequest("700Mi");
    final ResourceRequirements destResourceRequirements = new ResourceRequirements()
        .withCpuLimit("0.8")
        .withCpuRequest("0.8")
        .withMemoryLimit("800Mi")
        .withMemoryRequest("800Mi");

    jobCreator.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME,
        List.of(STANDARD_SYNC_OPERATION),
        new ActorDefinitionResourceRequirements().withDefault(sourceResourceRequirements),
        new ActorDefinitionResourceRequirements().withJobSpecific(List.of(
            new JobTypeResourceLimit().withJobType(JobType.SYNC).withResourceRequirements(destResourceRequirements))));

    final JobSyncConfig expectedJobSyncConfig = new JobSyncConfig()
        .withNamespaceDefinition(STANDARD_SYNC.getNamespaceDefinition())
        .withNamespaceFormat(STANDARD_SYNC.getNamespaceFormat())
        .withPrefix(STANDARD_SYNC.getPrefix())
        .withSourceConfiguration(SOURCE_CONNECTION.getConfiguration())
        .withSourceDockerImage(SOURCE_IMAGE_NAME)
        .withDestinationConfiguration(DESTINATION_CONNECTION.getConfiguration())
        .withDestinationDockerImage(DESTINATION_IMAGE_NAME)
        .withConfiguredAirbyteCatalog(STANDARD_SYNC.getCatalog())
        .withOperationSequence(List.of(STANDARD_SYNC_OPERATION))
        .withResourceRequirements(workerResourceRequirements)
        .withSourceResourceRequirements(sourceResourceRequirements)
        .withDestinationResourceRequirements(destResourceRequirements);

    final JobConfig expectedJobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.SYNC)
        .withSync(expectedJobSyncConfig);

    final String expectedScope = STANDARD_SYNC.getConnectionId().toString();

    verify(jobPersistence, times(1)).enqueueJob(expectedScope, expectedJobConfig);
  }

  @Test
  void testCreateResetConnectionJob() throws IOException {
    final List<StreamDescriptor> streamsToReset = List.of(STREAM1_DESCRIPTOR, STREAM2_DESCRIPTOR);
    final ConfiguredAirbyteCatalog expectedCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withStream(CatalogHelpers.createAirbyteStream(STREAM1_NAME, Field.of(FIELD_NAME, JsonSchemaType.STRING)))
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE),
        new ConfiguredAirbyteStream()
            .withStream(CatalogHelpers.createAirbyteStream(STREAM2_NAME, NAMESPACE, Field.of(FIELD_NAME, JsonSchemaType.STRING)))
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE),
        // this stream is not being reset, so it should have APPEND destination sync mode
        new ConfiguredAirbyteStream()
            .withStream(CatalogHelpers.createAirbyteStream(STREAM3_NAME, NAMESPACE, Field.of(FIELD_NAME, JsonSchemaType.STRING)))
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)));

    final State connectionState = new State().withState(Jsons.jsonNode(Map.of("key", "val")));
    when(statePersistence.getCurrentState(STANDARD_SYNC.getConnectionId()))
        .thenReturn(StateMessageHelper.getTypedState(connectionState.getState(), false));

    final JobResetConnectionConfig jobResetConnectionConfig = new JobResetConnectionConfig()
        .withNamespaceDefinition(STANDARD_SYNC.getNamespaceDefinition())
        .withNamespaceFormat(STANDARD_SYNC.getNamespaceFormat())
        .withPrefix(STANDARD_SYNC.getPrefix())
        .withDestinationConfiguration(DESTINATION_CONNECTION.getConfiguration())
        .withDestinationDockerImage(DESTINATION_IMAGE_NAME)
        .withConfiguredAirbyteCatalog(expectedCatalog)
        .withOperationSequence(List.of(STANDARD_SYNC_OPERATION))
        .withResourceRequirements(workerResourceRequirements)
        .withResetSourceConfiguration(new ResetSourceConfiguration().withStreamsToReset(streamsToReset))
        .withState(connectionState);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.RESET_CONNECTION)
        .withResetConnection(jobResetConnectionConfig);

    final String expectedScope = STANDARD_SYNC.getConnectionId().toString();
    when(jobPersistence.enqueueJob(expectedScope, jobConfig)).thenReturn(Optional.of(JOB_ID));

    final Optional<Long> jobId = jobCreator.createResetConnectionJob(
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        DESTINATION_IMAGE_NAME,
        List.of(STANDARD_SYNC_OPERATION),
        streamsToReset);

    verify(jobPersistence).enqueueJob(expectedScope, jobConfig);
    assertTrue(jobId.isPresent());
    assertEquals(JOB_ID, jobId.get());
  }

  @Test
  void testCreateResetConnectionJobEnsureNoQueuing() throws IOException {
    final List<StreamDescriptor> streamsToReset = List.of(STREAM1_DESCRIPTOR, STREAM2_DESCRIPTOR);
    final ConfiguredAirbyteCatalog expectedCatalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withStream(CatalogHelpers.createAirbyteStream(STREAM1_NAME, Field.of(FIELD_NAME, JsonSchemaType.STRING)))
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE),
        new ConfiguredAirbyteStream()
            .withStream(CatalogHelpers.createAirbyteStream(STREAM2_NAME, NAMESPACE, Field.of(FIELD_NAME, JsonSchemaType.STRING)))
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE),
        // this stream is not being reset, so it should have APPEND destination sync mode
        new ConfiguredAirbyteStream()
            .withStream(CatalogHelpers.createAirbyteStream(STREAM3_NAME, NAMESPACE, Field.of(FIELD_NAME, JsonSchemaType.STRING)))
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)));

    final State connectionState = new State().withState(Jsons.jsonNode(Map.of("key", "val")));
    when(statePersistence.getCurrentState(STANDARD_SYNC.getConnectionId()))
        .thenReturn(StateMessageHelper.getTypedState(connectionState.getState(), false));

    final JobResetConnectionConfig jobResetConnectionConfig = new JobResetConnectionConfig()
        .withNamespaceDefinition(STANDARD_SYNC.getNamespaceDefinition())
        .withNamespaceFormat(STANDARD_SYNC.getNamespaceFormat())
        .withPrefix(STANDARD_SYNC.getPrefix())
        .withDestinationConfiguration(DESTINATION_CONNECTION.getConfiguration())
        .withDestinationDockerImage(DESTINATION_IMAGE_NAME)
        .withConfiguredAirbyteCatalog(expectedCatalog)
        .withOperationSequence(List.of(STANDARD_SYNC_OPERATION))
        .withResourceRequirements(workerResourceRequirements)
        .withResetSourceConfiguration(new ResetSourceConfiguration().withStreamsToReset(streamsToReset))
        .withState(connectionState);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.RESET_CONNECTION)
        .withResetConnection(jobResetConnectionConfig);

    final String expectedScope = STANDARD_SYNC.getConnectionId().toString();
    when(jobPersistence.enqueueJob(expectedScope, jobConfig)).thenReturn(Optional.empty());

    final Optional<Long> jobId = jobCreator.createResetConnectionJob(
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        DESTINATION_IMAGE_NAME,
        List.of(STANDARD_SYNC_OPERATION),
        streamsToReset);

    verify(jobPersistence).enqueueJob(expectedScope, jobConfig);
    assertTrue(jobId.isEmpty());
  }

}
