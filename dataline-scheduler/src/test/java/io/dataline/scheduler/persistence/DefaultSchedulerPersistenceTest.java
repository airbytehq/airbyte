/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
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

package io.dataline.scheduler.persistence;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.dataline.commons.json.Jsons;
import io.dataline.config.Column;
import io.dataline.config.DataType;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.JobCheckConnectionConfig;
import io.dataline.config.JobConfig;
import io.dataline.config.JobDiscoverSchemaConfig;
import io.dataline.config.JobOutput;
import io.dataline.config.JobSyncConfig;
import io.dataline.config.Schema;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.Table;
import io.dataline.db.DatabaseHelper;
import io.dataline.scheduler.Job;
import io.dataline.scheduler.JobStatus;
import io.dataline.integrations.Integrations;
import io.dataline.scheduler.JobLogs;
import io.dataline.scheduler.ScopeHelper;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Record;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class DefaultSchedulerPersistenceTest {

  @SuppressWarnings("rawtypes")
  private static PostgreSQLContainer container;
  private static BasicDataSource connectionPool;

  private static final SourceConnectionImplementation SOURCE_CONNECTION_IMPLEMENTATION;
  private static final DestinationConnectionImplementation DESTINATION_CONNECTION_IMPLEMENTATION;
  private static final StandardSync STANDARD_SYNC;
  private static final Instant NOW;

  private SchedulerPersistence schedulerPersistence;

  private Supplier<Instant> timeSupplier;

  static {
    final UUID workspaceId = UUID.randomUUID();
    final UUID sourceImplementationId = UUID.randomUUID();
    final UUID sourceSpecificationId = Integrations.POSTGRES_TAP.getSpecId();

    JsonNode implementationJson = Jsons.jsonNode(ImmutableMap.builder()
        .put("apiKey", "123-abc")
        .put("hostname", "dataline.io")
        .build());

    SOURCE_CONNECTION_IMPLEMENTATION = new SourceConnectionImplementation()
        .withWorkspaceId(workspaceId)
        .withSourceSpecificationId(sourceSpecificationId)
        .withSourceImplementationId(sourceImplementationId)
        .withConfiguration(implementationJson)
        .withTombstone(false);

    final UUID destinationImplementationId = UUID.randomUUID();
    final UUID destinationSpecificationId = Integrations.POSTGRES_TARGET.getSpecId();

    DESTINATION_CONNECTION_IMPLEMENTATION = new DestinationConnectionImplementation()
        .withWorkspaceId(workspaceId)
        .withDestinationSpecificationId(destinationSpecificationId)
        .withDestinationImplementationId(destinationImplementationId)
        .withConfiguration(implementationJson);

    final Column column = new Column()
        .withDataType(DataType.STRING)
        .withName("id")
        .withSelected(true);

    final Table table = new Table()
        .withName("users")
        .withColumns(Lists.newArrayList(column))
        .withSelected(true);

    final Schema schema = new Schema()
        .withTables(Lists.newArrayList(table));

    final UUID connectionId = UUID.randomUUID();

    STANDARD_SYNC = new StandardSync()
        .withConnectionId(connectionId)
        .withName("presto to hudi")
        .withStatus(StandardSync.Status.ACTIVE)
        .withSchema(schema)
        .withSourceImplementationId(sourceImplementationId)
        .withDestinationImplementationId(destinationImplementationId)
        .withSyncMode(StandardSync.SyncMode.APPEND);

    NOW = Instant.now();
  }

  @SuppressWarnings("rawtypes")
  @BeforeAll
  public static void dbSetup() throws IOException, InterruptedException {
    container = new PostgreSQLContainer("postgres:13-alpine")
        .withDatabaseName("dataline")
        .withUsername("docker")
        .withPassword("docker");
    container.start();

    container.copyFileToContainer(MountableFile.forClasspathResource("schema.sql"), "/etc/init.sql");
    // execInContainer uses Docker's EXEC so it needs to be split up like this
    container.execInContainer("psql", "-d", "dataline", "-U", "docker", "-a", "-f", "/etc/init.sql");

    connectionPool =
        DatabaseHelper.getConnectionPool(
            container.getUsername(), container.getPassword(), container.getJdbcUrl());
  }

  @AfterAll
  public static void tearDown() {
    container.stop();
  }

  @SuppressWarnings("unchecked")
  @BeforeEach
  public void setup() throws SQLException {
    // todo (cgardens) - truncate whole db.
    DatabaseHelper.query(connectionPool, ctx -> ctx.execute("DELETE FROM jobs"));

    timeSupplier = mock(Supplier.class);
    when(timeSupplier.get()).thenReturn(NOW);

    schedulerPersistence = new DefaultSchedulerPersistence(connectionPool, timeSupplier);
  }

  private Record getJobRecord(long jobId) throws SQLException {
    return DatabaseHelper.query(
        connectionPool,
        ctx -> ctx.fetch("SELECT * FROM jobs WHERE id = ?", jobId).stream()
            .findFirst()
            .orElseThrow(
                () -> new RuntimeException("Could not find job with id: " + jobId)));
  }

  @Test
  public void testCreateSourceCheckConnectionJob() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createSourceCheckConnectionJob(SOURCE_CONNECTION_IMPLEMENTATION);

    final Record jobEntry = getJobRecord(jobId);

    final String imageName = Integrations.findBySpecId(SOURCE_CONNECTION_IMPLEMENTATION.getSourceSpecificationId()).getDiscoverSchemaImage();
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(SOURCE_CONNECTION_IMPLEMENTATION.getConfiguration())
        .withDockerImage(imageName);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.CHECK_CONNECTION_SOURCE)
        .withCheckConnection(jobCheckConnectionConfig);

    assertJobConfigEqualJobDbRecord(jobId, SOURCE_CONNECTION_IMPLEMENTATION.getSourceImplementationId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testCreateDestinationCheckConnectionJob() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createDestinationCheckConnectionJob(DESTINATION_CONNECTION_IMPLEMENTATION);

    final Record jobEntry = getJobRecord(jobId);

    final String imageName = Integrations.findBySpecId(DESTINATION_CONNECTION_IMPLEMENTATION.getDestinationSpecificationId())
        .getDiscoverSchemaImage();
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig()
        .withConnectionConfiguration(DESTINATION_CONNECTION_IMPLEMENTATION.getConfiguration())
        .withDockerImage(imageName);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.CHECK_CONNECTION_DESTINATION)
        .withCheckConnection(jobCheckConnectionConfig);

    assertJobConfigEqualJobDbRecord(jobId, DESTINATION_CONNECTION_IMPLEMENTATION.getDestinationImplementationId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testCreateDiscoverSchemaJob() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createDiscoverSchemaJob(SOURCE_CONNECTION_IMPLEMENTATION);

    final Record jobEntry = getJobRecord(jobId);

    final String imageName = Integrations.findBySpecId(SOURCE_CONNECTION_IMPLEMENTATION.getSourceSpecificationId()).getDiscoverSchemaImage();
    final JobDiscoverSchemaConfig jobDiscoverSchemaConfig = new JobDiscoverSchemaConfig()
        .withConnectionConfiguration(SOURCE_CONNECTION_IMPLEMENTATION.getConfiguration())
        .withDockerImage(imageName);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.DISCOVER_SCHEMA)
        .withDiscoverSchema(jobDiscoverSchemaConfig);

    assertJobConfigEqualJobDbRecord(jobId, SOURCE_CONNECTION_IMPLEMENTATION.getSourceImplementationId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testCreateSyncJob() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION_IMPLEMENTATION,
        DESTINATION_CONNECTION_IMPLEMENTATION,
        STANDARD_SYNC);

    final Record jobEntry = getJobRecord(jobId);

    final String sourceImageName = Integrations.findBySpecId(SOURCE_CONNECTION_IMPLEMENTATION.getSourceSpecificationId()).getSyncImage();
    final String destinationImageName = Integrations.findBySpecId(DESTINATION_CONNECTION_IMPLEMENTATION.getDestinationSpecificationId())
        .getSyncImage();
    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withSourceConnectionImplementation(SOURCE_CONNECTION_IMPLEMENTATION)
        .withSourceDockerImage(sourceImageName)
        .withDestinationConnectionImplementation(DESTINATION_CONNECTION_IMPLEMENTATION)
        .withDestinationDockerImage(destinationImageName)
        .withStandardSync(STANDARD_SYNC);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.SYNC)
        .withSync(jobSyncConfig);

    assertJobConfigEqualJobDbRecord(jobId, STANDARD_SYNC.getConnectionId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testGetJob() throws IOException {
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION_IMPLEMENTATION,
        DESTINATION_CONNECTION_IMPLEMENTATION,
        STANDARD_SYNC);

    when(timeSupplier.get()).thenReturn(NOW);

    final Job actual = schedulerPersistence.getJob(jobId);

    final Job expected = getExpectedJob(jobId);

    assertEquals(expected, actual);
  }

  @Test
  void testUpdateStatus() throws IOException {
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION_IMPLEMENTATION,
        DESTINATION_CONNECTION_IMPLEMENTATION,
        STANDARD_SYNC);

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
        SOURCE_CONNECTION_IMPLEMENTATION,
        DESTINATION_CONNECTION_IMPLEMENTATION,
        STANDARD_SYNC);

    when(timeSupplier.get()).thenReturn(Instant.ofEpochMilli(4242));
    final JobOutput jobOutput = new JobOutput().withOutputType(JobOutput.OutputType.DISCOVER_SCHEMA);
    schedulerPersistence.writeOutput(jobId, jobOutput);

    final Job updated = schedulerPersistence.getJob(jobId);

    assertEquals(Optional.of(jobOutput), updated.getOutput());
  }

  @Test
  public void testListJobs() throws IOException {
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION_IMPLEMENTATION,
        DESTINATION_CONNECTION_IMPLEMENTATION,
        STANDARD_SYNC);

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
    final long discoverSchemaJobId = schedulerPersistence.createDiscoverSchemaJob(SOURCE_CONNECTION_IMPLEMENTATION);

    // sync job that is not failed.
    schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION_IMPLEMENTATION,
        DESTINATION_CONNECTION_IMPLEMENTATION,
        STANDARD_SYNC);

    // sync job that has failed.
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION_IMPLEMENTATION,
        DESTINATION_CONNECTION_IMPLEMENTATION,
        STANDARD_SYNC);

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
    schedulerPersistence.createSyncJob(SOURCE_CONNECTION_IMPLEMENTATION, DESTINATION_CONNECTION_IMPLEMENTATION, STANDARD_SYNC);
    final Instant afterNow = NOW.plusSeconds(1000);
    when(timeSupplier.get()).thenReturn(afterNow);
    final long jobId = schedulerPersistence.createSyncJob(SOURCE_CONNECTION_IMPLEMENTATION, DESTINATION_CONNECTION_IMPLEMENTATION, STANDARD_SYNC);

    final Optional<Job> actual = schedulerPersistence.getLastSyncJob(STANDARD_SYNC.getConnectionId());

    final String sourceImageName = Integrations.findBySpecId(SOURCE_CONNECTION_IMPLEMENTATION.getSourceSpecificationId()).getSyncImage();
    final String destinationImageName =
        Integrations.findBySpecId(DESTINATION_CONNECTION_IMPLEMENTATION.getDestinationSpecificationId()).getSyncImage();
    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withSourceConnectionImplementation(SOURCE_CONNECTION_IMPLEMENTATION)
        .withSourceDockerImage(sourceImageName)
        .withDestinationConnectionImplementation(DESTINATION_CONNECTION_IMPLEMENTATION)
        .withDestinationDockerImage(destinationImageName)
        .withStandardSync(STANDARD_SYNC);

    final JobConfig jobConfig = new JobConfig()
        .withConfigType(JobConfig.ConfigType.SYNC)
        .withSync(jobSyncConfig);

    final String scope = ScopeHelper.createScope(JobConfig.ConfigType.SYNC, STANDARD_SYNC.getConnectionId().toString());

    final Job expected = new Job(
        jobId,
        scope,
        jobConfig, JobLogs.getLogDirectory(scope), null, 0, JobStatus.PENDING,
        null, afterNow.getEpochSecond(),
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
        SOURCE_CONNECTION_IMPLEMENTATION,
        DESTINATION_CONNECTION_IMPLEMENTATION,
        STANDARD_SYNC);
    final Instant afterNow = NOW.plusSeconds(1000);
    when(timeSupplier.get()).thenReturn(afterNow);
    schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION_IMPLEMENTATION,
        DESTINATION_CONNECTION_IMPLEMENTATION,
        STANDARD_SYNC);

    final Optional<Job> actual = schedulerPersistence.getOldestPendingJob();

    assertTrue(actual.isPresent());
    assertEquals(getExpectedJob(jobId), actual.get());
  }

  @Test
  public void testGetOldestPendingJobOnlyPendingJobs() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createSyncJob(
        SOURCE_CONNECTION_IMPLEMENTATION,
        DESTINATION_CONNECTION_IMPLEMENTATION,
        STANDARD_SYNC);

    DatabaseHelper.query(
        connectionPool,
        ctx -> ctx.execute("UPDATE jobs SET status = CAST(? AS JOB_STATUS) WHERE id = ?", JobStatus.COMPLETED.toString().toLowerCase(), jobId));

    final Optional<Job> actual = schedulerPersistence.getOldestPendingJob();

    assertTrue(actual.isEmpty());
  }

  @Test
  public void testGetJobFromRecord() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createSyncJob(SOURCE_CONNECTION_IMPLEMENTATION, DESTINATION_CONNECTION_IMPLEMENTATION, STANDARD_SYNC);
    final Record jobRecord = getJobRecord(jobId);

    final Job actual = DefaultSchedulerPersistence.getJobFromRecord(jobRecord);
    final Job expected = getExpectedJob(jobId);

    assertEquals(expected, actual);
  }

  private static void assertJobConfigEqualJobDbRecord(long jobId, String configId, JobConfig expected, Record actual) {
    final String scope = ScopeHelper.createScope(expected.getConfigType(), configId);
    assertEquals(jobId, actual.get("id"));
    assertEquals(scope, actual.get("scope"));
    assertEquals("pending", actual.get("status", String.class));
    assertEquals(JobLogs.getLogDirectory(scope), actual.get("stdout_path", String.class));
    assertEquals(JobLogs.getLogDirectory(scope), actual.get("stderr_path", String.class));
    assertEquals(NOW.getEpochSecond(), actual.getValue("created_at", LocalDateTime.class).toEpochSecond(ZoneOffset.UTC));
    assertNull(actual.getValue("started_at", LocalDateTime.class));
    assertEquals(NOW.getEpochSecond(), actual.getValue("updated_at", LocalDateTime.class).toEpochSecond(ZoneOffset.UTC));
    assertNull(actual.get("output"));
    assertEquals(expected, Jsons.deserialize(actual.get("config", String.class), JobConfig.class));
  }

  private Job getExpectedJob(long jobId) {
    return getExpectedJob(jobId, JobStatus.PENDING);
  }

  private Job getExpectedJob(long jobId, JobStatus jobStatus) {
    final String sourceImageName = Integrations.findBySpecId(SOURCE_CONNECTION_IMPLEMENTATION.getSourceSpecificationId())
        .getDiscoverSchemaImage();
    final String destinationImageName = Integrations.findBySpecId(DESTINATION_CONNECTION_IMPLEMENTATION.getDestinationSpecificationId())
        .getDiscoverSchemaImage();

    final JobSyncConfig jobSyncConfig = new JobSyncConfig()
        .withSourceDockerImage(sourceImageName)
        .withDestinationDockerImage(destinationImageName)
        .withSourceConnectionImplementation(SOURCE_CONNECTION_IMPLEMENTATION)
        .withDestinationConnectionImplementation(DESTINATION_CONNECTION_IMPLEMENTATION)
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
        JobLogs.getLogDirectory(scope),
        null,
        0,
        jobStatus,
        null,
        NOW.getEpochSecond(),
        NOW.getEpochSecond());
  }

}
