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

package io.airbyte.scheduler.persistence;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobResetConnectionConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.JobSyncConfig.NamespaceDefinitionType;
import io.airbyte.config.OperatorNormalization;
import io.airbyte.config.OperatorNormalization.Option;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSyncOperation;
import io.airbyte.config.StandardSyncOperation.OperatorType;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.DestinationSyncMode;
import io.airbyte.protocol.models.Field;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.io.IOException;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class DefaultJobCreatorTest {

  private static final String STREAM_NAME = "users";
  private static final String FIELD_NAME = "id";

  private static final String SOURCE_IMAGE_NAME = "daxtarity/sourceimagename";
  private static final String DESTINATION_IMAGE_NAME = "daxtarity/destinationimagename";
  private static final SourceConnection SOURCE_CONNECTION;
  private static final DestinationConnection DESTINATION_CONNECTION;
  private static final StandardSync STANDARD_SYNC;
  private static final StandardSyncOperation STANDARD_SYNC_OPERATION;
  private static final long JOB_ID = 12L;

  private JobPersistence jobPersistence;
  private JobCreator jobCreator;

  static {
    final UUID workspaceId = UUID.randomUUID();
    final UUID sourceId = UUID.randomUUID();
    final UUID sourceDefinitionId = UUID.randomUUID();

    JsonNode implementationJson = Jsons.jsonNode(ImmutableMap.builder()
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

    final ConfiguredAirbyteStream stream = new ConfiguredAirbyteStream()
        .withStream(CatalogHelpers.createAirbyteStream(STREAM_NAME, Field.of(FIELD_NAME, JsonSchemaPrimitive.STRING)));
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(Collections.singletonList(stream));

    final UUID connectionId = UUID.randomUUID();
    final UUID operationId = UUID.randomUUID();

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
  void setup() throws IOException {
    jobPersistence = mock(JobPersistence.class);
    jobCreator = new DefaultJobCreator(jobPersistence);
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
        .withOperationSequence(List.of(STANDARD_SYNC_OPERATION));

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
        List.of(STANDARD_SYNC_OPERATION)).orElseThrow();
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
        .withOperationSequence(List.of(STANDARD_SYNC_OPERATION));

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
        List.of(STANDARD_SYNC_OPERATION)).isEmpty());
  }

  @Test
  void testCreateResetConnectionJob() throws IOException {
    final ConfiguredAirbyteCatalog expectedCatalog = STANDARD_SYNC.getCatalog();
    expectedCatalog.getStreams()
        .forEach(configuredAirbyteStream -> {
          configuredAirbyteStream.setSyncMode(io.airbyte.protocol.models.SyncMode.FULL_REFRESH);
          configuredAirbyteStream.setDestinationSyncMode(DestinationSyncMode.OVERWRITE);
        });

    final JobResetConnectionConfig JobResetConnectionConfig = new JobResetConnectionConfig()
        .withNamespaceDefinition(STANDARD_SYNC.getNamespaceDefinition())
        .withNamespaceFormat(STANDARD_SYNC.getNamespaceFormat())
        .withPrefix(STANDARD_SYNC.getPrefix())
        .withDestinationConfiguration(DESTINATION_CONNECTION.getConfiguration())
        .withDestinationDockerImage(DESTINATION_IMAGE_NAME)
        .withConfiguredAirbyteCatalog(expectedCatalog)
        .withOperationSequence(List.of(STANDARD_SYNC_OPERATION));

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.RESET_CONNECTION)
        .withResetConnection(JobResetConnectionConfig);

    final String expectedScope = STANDARD_SYNC.getConnectionId().toString();
    when(jobPersistence.enqueueJob(expectedScope, jobConfig)).thenReturn(Optional.of(JOB_ID));

    final long jobId = jobCreator.createResetConnectionJob(
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        DESTINATION_IMAGE_NAME,
        List.of(STANDARD_SYNC_OPERATION)).orElseThrow();
    assertEquals(JOB_ID, jobId);
  }

  @Test
  void testCreateResetConnectionJobEnsureNoQueuing() throws IOException {
    final ConfiguredAirbyteCatalog expectedCatalog = STANDARD_SYNC.getCatalog();
    expectedCatalog.getStreams()
        .forEach(configuredAirbyteStream -> {
          configuredAirbyteStream.setSyncMode(io.airbyte.protocol.models.SyncMode.FULL_REFRESH);
          configuredAirbyteStream.setDestinationSyncMode(DestinationSyncMode.OVERWRITE);
        });

    final JobResetConnectionConfig JobResetConnectionConfig = new JobResetConnectionConfig()
        .withNamespaceDefinition(STANDARD_SYNC.getNamespaceDefinition())
        .withNamespaceFormat(STANDARD_SYNC.getNamespaceFormat())
        .withPrefix(STANDARD_SYNC.getPrefix())
        .withDestinationConfiguration(DESTINATION_CONNECTION.getConfiguration())
        .withDestinationDockerImage(DESTINATION_IMAGE_NAME)
        .withConfiguredAirbyteCatalog(expectedCatalog)
        .withOperationSequence(List.of(STANDARD_SYNC_OPERATION));

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(ConfigType.RESET_CONNECTION)
        .withResetConnection(JobResetConnectionConfig);

    final String expectedScope = STANDARD_SYNC.getConnectionId().toString();
    when(jobPersistence.enqueueJob(expectedScope, jobConfig)).thenReturn(Optional.empty());

    assertTrue(jobCreator.createResetConnectionJob(
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        DESTINATION_IMAGE_NAME,
        List.of(STANDARD_SYNC_OPERATION)).isEmpty());
  }

}
