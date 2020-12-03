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
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.DataType;
import io.airbyte.config.DestinationConnection;
import io.airbyte.config.Field;
import io.airbyte.config.JobCheckConnectionConfig;
import io.airbyte.config.JobConfig;
import io.airbyte.config.JobConfig.ConfigType;
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.Schema;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.SyncMode;
import io.airbyte.config.Stream;
import io.airbyte.scheduler.ScopeHelper;
import java.io.IOException;
import java.util.UUID;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

public class DefaultJobCreatorTest {

  private static final String SOURCE_IMAGE_NAME = "daxtarity/sourceimagename";
  private static final String DESTINATION_IMAGE_NAME = "daxtarity/destinationimagename";
  private static final SourceConnection SOURCE_CONNECTION;
  private static final DestinationConnection DESTINATION_CONNECTION;
  private static final StandardSync STANDARD_SYNC;
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

    final Field field = new Field()
        .withDataType(DataType.STRING)
        .withName("id")
        .withSelected(true);

    final Stream stream = new Stream()
        .withName("users")
        .withFields(Lists.newArrayList(field))
        .withSelected(true);

    final Schema schema = new Schema()
        .withStreams(Lists.newArrayList(stream));

    final UUID connectionId = UUID.randomUUID();

    STANDARD_SYNC = new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi")
        .withStatus(StandardSync.Status.ACTIVE)
        .withSchema(schema)
        .withSourceId(sourceId)
        .withDestinationId(destinationId)
        .withSyncMode(SyncMode.FULL_REFRESH);
  }

  @BeforeEach
  void setup() {
    jobPersistence = mock(JobPersistence.class);
    jobCreator = new DefaultJobCreator(jobPersistence);
  }

  @Test
  void testCreateSourceCheckConnectionJob() throws IOException {
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(SOURCE_CONNECTION.getConfiguration())
        .withDockerImage(SOURCE_IMAGE_NAME);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.CHECK_CONNECTION_SOURCE)
        .withCheckConnection(jobCheckConnectionConfig);

    final String expectedScope = ScopeHelper.createScope(ConfigType.CHECK_CONNECTION_SOURCE, SOURCE_CONNECTION.getSourceId().toString());
    when(jobPersistence.createJob(expectedScope, jobConfig)).thenReturn(JOB_ID);

    final long jobId = jobCreator.createSourceCheckConnectionJob(SOURCE_CONNECTION, SOURCE_IMAGE_NAME);
    assertEquals(JOB_ID, jobId);
  }

  @Test
  void testCreateDestinationCheckConnectionJob() throws IOException {
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(DESTINATION_CONNECTION.getConfiguration())
        .withDockerImage(DESTINATION_IMAGE_NAME);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.CHECK_CONNECTION_DESTINATION)
        .withCheckConnection(jobCheckConnectionConfig);

    final String expectedScope =
        ScopeHelper.createScope(ConfigType.CHECK_CONNECTION_DESTINATION, DESTINATION_CONNECTION.getDestinationId().toString());
    when(jobPersistence.createJob(expectedScope, jobConfig)).thenReturn(JOB_ID);

    final long jobId = jobCreator.createDestinationCheckConnectionJob(DESTINATION_CONNECTION, DESTINATION_IMAGE_NAME);
    assertEquals(JOB_ID, jobId);
  }

  @Test
  void testCreateDiscoverSchemaJob() throws IOException {
    final JobDiscoverCatalogConfig jobDiscoverCatalogConfig = new JobDiscoverCatalogConfig()
        .withConnectionConfiguration(SOURCE_CONNECTION.getConfiguration())
        .withDockerImage(SOURCE_IMAGE_NAME);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.DISCOVER_SCHEMA)
        .withDiscoverCatalog(jobDiscoverCatalogConfig);

    final String expectedScope = ScopeHelper.createScope(ConfigType.DISCOVER_SCHEMA, SOURCE_CONNECTION.getSourceId().toString());
    when(jobPersistence.createJob(expectedScope, jobConfig)).thenReturn(JOB_ID);

    final long jobId = jobCreator.createDiscoverSchemaJob(SOURCE_CONNECTION, SOURCE_IMAGE_NAME);
    assertEquals(JOB_ID, jobId);
  }

  @Test
  void testCreateGetSpecJob() throws IOException {
    final String integrationImage = "pg/pg-3000";

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.GET_SPEC)
        .withGetSpec(new JobGetSpecConfig().withDockerImage(integrationImage));

    final String expectedScope = ScopeHelper.createScope(ConfigType.GET_SPEC, integrationImage);
    when(jobPersistence.createJob(expectedScope, jobConfig)).thenReturn(JOB_ID);

    final long jobId = jobCreator.createGetSpecJob(integrationImage);
    assertEquals(JOB_ID, jobId);
  }

  @Test
  void testCreateSyncJob() throws IOException {
    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withSourceConnection(SOURCE_CONNECTION)
        .withSourceDockerImage(SOURCE_IMAGE_NAME)
        .withDestinationConnection(DESTINATION_CONNECTION)
        .withDestinationDockerImage(DESTINATION_IMAGE_NAME)
        .withStandardSync(STANDARD_SYNC);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.SYNC)
        .withSync(jobSyncConfig);

    final String expectedScope = ScopeHelper.createScope(ConfigType.SYNC, STANDARD_SYNC.getConnectionId().toString());
    when(jobPersistence.createJob(expectedScope, jobConfig)).thenReturn(JOB_ID);

    final long jobId = jobCreator.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME);
    assertEquals(JOB_ID, jobId);
  }

}
