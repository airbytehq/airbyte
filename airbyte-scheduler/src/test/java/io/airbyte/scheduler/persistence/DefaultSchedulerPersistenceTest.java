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
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
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
import io.airbyte.config.JobDiscoverCatalogConfig;
import io.airbyte.config.JobGetSpecConfig;
import io.airbyte.config.JobOutput;
import io.airbyte.config.JobSyncConfig;
import io.airbyte.config.Schema;
import io.airbyte.config.SourceConnection;
import io.airbyte.config.StandardSync;
import io.airbyte.config.StandardSync.SyncMode;
import io.airbyte.config.Stream;
import io.airbyte.db.Database;
import io.airbyte.db.Databases;
import io.airbyte.scheduler.Job;
import io.airbyte.scheduler.JobStatus;
import io.airbyte.scheduler.ScopeHelper;
import java.io.IOException;
import java.nio.file.Path;
import java.sql.SQLException;
import java.time.Instant;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import org.jooq.Record;
import org.jooq.Result;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

class DefaultSchedulerPersistenceTest {

  @SuppressWarnings("rawtypes")
  private static PostgreSQLContainer container;
  private static Database database;

  private static final String SOURCE_IMAGE_NAME = "daxtarity/sourceimagename";
  private static final String DESTINATION_IMAGE_NAME = "daxtarity/destinationimagename";
  private static final SourceConnection SOURCE_CONNECTION;
  private static final DestinationConnection DESTINATION_CONNECTION;
  private static final StandardSync STANDARD_SYNC;
  private static final Instant NOW;

  private SchedulerPersistence schedulerPersistence;

  private Supplier<Instant> timeSupplier;

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

    NOW = Instant.now();
  }

  @SuppressWarnings("rawtypes")
  @BeforeAll
  public static void dbSetup() throws IOException, InterruptedException {
    container = new PostgreSQLContainer("postgres:13-alpine")
        .withDatabaseName("airbyte")
        .withUsername("docker")
        .withPassword("docker");
    container.start();

    container.copyFileToContainer(MountableFile.forClasspathResource("schema.sql"), "/etc/init.sql");
    // execInContainer uses Docker's EXEC so it needs to be split up like this
    container.execInContainer("psql", "-d", "airbyte", "-U", "docker", "-a", "-f", "/etc/init.sql");

    database = Databases.createPostgresDatabase(container.getUsername(), container.getPassword(), container.getJdbcUrl());
  }

  @AfterAll
  public static void tearDown() {
    container.stop();
  }

  @SuppressWarnings("unchecked")
  @BeforeEach
  public void setup() throws SQLException {
    // todo (cgardens) - truncate whole db.
    database.query(ctx -> ctx.execute("DELETE FROM jobs"));

    timeSupplier = mock(Supplier.class);
    when(timeSupplier.get()).thenReturn(NOW);

    schedulerPersistence = new DefaultSchedulerPersistence(database, timeSupplier);
  }

  private Result<Record> getJobRecord(long jobId) throws SQLException {
    return database.query(ctx -> ctx.fetch(DefaultSchedulerPersistence.BASE_JOB_SELECT_AND_JOIN + "WHERE jobs.id = ?", jobId));
  }

  @Test
  public void testCreateSourceCheckConnectionJob() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createSourceCheckConnectionJob(SOURCE_CONNECTION, SOURCE_IMAGE_NAME);

    final Result<Record> jobEntry = getJobRecord(jobId);

    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(SOURCE_CONNECTION.getConfiguration())
        .withDockerImage(SOURCE_IMAGE_NAME);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.CHECK_CONNECTION_SOURCE)
        .withCheckConnection(jobCheckConnectionConfig);

    assertJobConfigEqualJobDbRecord(jobId, SOURCE_CONNECTION.getSourceId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testCreateDestinationCheckConnectionJob() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createDestinationCheckConnectionJob(DESTINATION_CONNECTION, DESTINATION_IMAGE_NAME);

    final Result<Record> jobEntry = getJobRecord(jobId);

    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(DESTINATION_CONNECTION.getConfiguration())
        .withDockerImage(DESTINATION_IMAGE_NAME);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.CHECK_CONNECTION_DESTINATION)
        .withCheckConnection(jobCheckConnectionConfig);

    assertJobConfigEqualJobDbRecord(jobId, DESTINATION_CONNECTION.getDestinationId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testCreateDiscoverSchemaJob() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createDiscoverSchemaJob(SOURCE_CONNECTION, SOURCE_IMAGE_NAME);

    final Result<Record> jobEntry = getJobRecord(jobId);

    final JobDiscoverCatalogConfig jobDiscoverCatalogConfig = new JobDiscoverCatalogConfig()
        .withConnectionConfiguration(SOURCE_CONNECTION.getConfiguration())
        .withDockerImage(SOURCE_IMAGE_NAME);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.DISCOVER_SCHEMA)
        .withDiscoverCatalog(jobDiscoverCatalogConfig);

    assertJobConfigEqualJobDbRecord(jobId, SOURCE_CONNECTION.getSourceId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testCreateGetSpecJob() throws IOException, SQLException {
    final String integrationImage = "thisdoesnotexist";
    final long jobId = schedulerPersistence.createGetSpecJob(integrationImage);

    final Result<Record> jobEntry = getJobRecord(jobId);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.GET_SPEC)
        .withGetSpec(new JobGetSpecConfig().withDockerImage(integrationImage));

    assertJobConfigEqualJobDbRecord(jobId, integrationImage, jobConfig, jobEntry);
  }

  @Test
  public void testCreateSyncJob() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME);

    final Result<Record> jobEntry = getJobRecord(jobId);

    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withSourceConnection(SOURCE_CONNECTION)
        .withSourceDockerImage(SOURCE_IMAGE_NAME)
        .withDestinationConnection(DESTINATION_CONNECTION)
        .withDestinationDockerImage(DESTINATION_IMAGE_NAME)
        .withStandardSync(STANDARD_SYNC);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.SYNC)
        .withSync(jobSyncConfig);

    assertJobConfigEqualJobDbRecord(jobId, STANDARD_SYNC.getConnectionId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testGetJob() throws IOException {
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME);

    when(timeSupplier.get()).thenReturn(NOW);

    final Job actual = schedulerPersistence.getJob(jobId);

    final Job expected = getExpectedJob(jobId);

    assertEquals(expected, actual);
  }

  @Test
  void testUpdateStatus() throws IOException {
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME);

    final Job created = schedulerPersistence.getJob(jobId);

    when(timeSupplier.get()).thenReturn(Instant.ofEpochMilli(4242));
    schedulerPersistence.updateStatus(jobId, JobStatus.FAILED);

    final Job updated = schedulerPersistence.getJob(jobId);

    assertEquals(JobStatus.FAILED, updated.getStatus());
    assertNotEquals(created.getUpdatedAtInSecond(), updated.getUpdatedAtInSecond());
  }

  @Test
  void testWriteOutput() throws IOException {
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME);
    final long attemptId = schedulerPersistence.createAttempt(jobId, Path.of("/blah"));

    when(timeSupplier.get()).thenReturn(Instant.ofEpochMilli(4242));
    final JobOutput jobOutput = new JobOutput().withOutputType(JobOutput.OutputType.DISCOVER_CATALOG);
    schedulerPersistence.writeOutput(jobId, attemptId, jobOutput);

    final Job updated = schedulerPersistence.getJob(jobId);
    assertEquals(Optional.of(jobOutput), updated.getAttempts().get(0).getOutput());
  }

  @Test
  public void testListJobs() throws IOException {
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME);

    final List<Job> actualList = schedulerPersistence
        .listJobs(JobConfig.ConfigType.SYNC, STANDARD_SYNC.getConnectionId().toString());

    final Job actual = actualList.get(0);
    final Job expected = getExpectedJob(jobId);

    assertEquals(1, actualList.size());
    assertEquals(expected, actual);
  }

  @Test
  public void testListJobsWithStatus() throws IOException {
    // non-sync job that has failed.
    final long discoverSchemaJobId = schedulerPersistence.createDiscoverSchemaJob(SOURCE_CONNECTION, SOURCE_IMAGE_NAME);

    // sync job that is not failed.
    schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME);

    // sync job that has failed.
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME);

    schedulerPersistence.updateStatus(discoverSchemaJobId, JobStatus.FAILED);
    schedulerPersistence.updateStatus(jobId, JobStatus.FAILED);

    final List<Job> actualList = schedulerPersistence.listJobsWithStatus(JobConfig.ConfigType.SYNC, JobStatus.FAILED);

    final Job actual = actualList.get(0);
    final Job expected = getExpectedJob(jobId, JobStatus.FAILED);

    assertEquals(1, actualList.size());
    assertEquals(expected, actual);
  }

  @Test
  public void testGetLastSyncJobForConnectionId() throws IOException {
    schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME);
    final Instant afterNow = NOW.plusSeconds(1000);
    when(timeSupplier.get()).thenReturn(afterNow);
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME);

    final Optional<Job> actual = schedulerPersistence.getLastSyncJob(STANDARD_SYNC.getConnectionId());

    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withSourceConnection(SOURCE_CONNECTION)
        .withSourceDockerImage(SOURCE_IMAGE_NAME)
        .withDestinationConnection(DESTINATION_CONNECTION)
        .withDestinationDockerImage(DESTINATION_IMAGE_NAME)
        .withStandardSync(STANDARD_SYNC);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.SYNC)
        .withSync(jobSyncConfig);

    final String scope = ScopeHelper.createScope(JobConfig.ConfigType.SYNC, STANDARD_SYNC.getConnectionId().toString());

    final Job expected = new Job(
        jobId,
        scope,
        jobConfig,
        Collections.emptyList(),
        JobStatus.PENDING,
        null,
        afterNow.getEpochSecond(),
        afterNow.getEpochSecond());

    assertTrue(actual.isPresent());
    assertEquals(expected, actual.get());
  }

  @Test
  public void testGetLastSyncJobForConnectionIdEmpty() throws IOException {
    final Optional<Job> actual = schedulerPersistence.getLastSyncJob(STANDARD_SYNC.getConnectionId());

    assertTrue(actual.isEmpty());
  }

  @Test
  public void testGetOldestPendingJob() throws IOException {
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME);
    final Instant afterNow = NOW.plusSeconds(1000);
    when(timeSupplier.get()).thenReturn(afterNow);
    schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME);

    final Optional<Job> actual = schedulerPersistence.getOldestPendingJob();

    assertTrue(actual.isPresent());
    assertEquals(getExpectedJob(jobId), actual.get());
  }

  @Test
  public void testGetOldestPendingJobOnlyPendingJobs() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME);

    database.query(
        ctx -> ctx.execute("UPDATE jobs SET status = CAST(? AS JOB_STATUS) WHERE id = ?", JobStatus.COMPLETED.toString().toLowerCase(), jobId));

    final Optional<Job> actual = schedulerPersistence.getOldestPendingJob();

    assertTrue(actual.isEmpty());
  }

  @Test
  public void testGetJobFromRecord() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION,
        DESTINATION_CONNECTION,
        STANDARD_SYNC,
        SOURCE_IMAGE_NAME,
        DESTINATION_IMAGE_NAME);

    final Job actual = DefaultSchedulerPersistence.getJobFromResult(getJobRecord(jobId)).get();
    final Job expected = getExpectedJob(jobId);

    assertEquals(expected, actual);
  }

  private static void assertJobConfigEqualJobDbRecord(long jobId, String configId, JobConfig expected, Result<Record> actual) {
    final String scope = ScopeHelper.createScope(expected.getConfigType(), configId);
    // todo cgardnes
    // assertEquals(jobId, actual.get("id"));
    // assertEquals(scope, actual.get("scope"));
    // assertEquals("pending", actual.get("status", String.class));
    // assertEquals(NOW.getEpochSecond(), actual.get("created_at",
    // LocalDateTime.class).toEpochSecond(ZoneOffset.UTC));
    // assertNull(actual.get("started_at", LocalDateTime.class));
    // assertEquals(NOW.getEpochSecond(), actual.get("updated_at",
    // LocalDateTime.class).toEpochSecond(ZoneOffset.UTC));
    // assertNull(actual.get("output"));
    // assertEquals(expected, Jsons.deserialize(actual.get("config", String.class), JobConfig.class));
  }

  private Job getExpectedJob(long jobId) {
    return getExpectedJob(jobId, JobStatus.PENDING);
  }

  private Job getExpectedJob(long jobId, JobStatus jobStatus) {
    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withSourceDockerImage(SOURCE_IMAGE_NAME)
        .withDestinationDockerImage(DESTINATION_IMAGE_NAME)
        .withSourceConnection(SOURCE_CONNECTION)
        .withDestinationConnection(DESTINATION_CONNECTION)
        .withState(null)
        .withStandardSync(STANDARD_SYNC);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.SYNC)
        .withSync(jobSyncConfig);

    final String scope = ScopeHelper.createScope(JobConfig.ConfigType.SYNC, STANDARD_SYNC.getConnectionId().toString());

    return new Job(
        jobId,
        scope,
        jobConfig,
        Collections.emptyList(),
        jobStatus,
        null,
        NOW.getEpochSecond(),
        NOW.getEpochSecond());
  }

}
