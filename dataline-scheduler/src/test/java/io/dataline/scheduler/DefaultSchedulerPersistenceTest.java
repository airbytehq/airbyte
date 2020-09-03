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

package io.dataline.scheduler;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

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
import io.dataline.config.JobSyncConfig;
import io.dataline.config.Schema;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.Table;
import io.dataline.db.DatabaseHelper;
import io.dataline.integrations.Integrations;
import java.io.IOException;
import java.sql.SQLException;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.function.Supplier;
import io.dataline.scheduler.persistence.DefaultSchedulerPersistence;
import io.dataline.scheduler.persistence.SchedulerPersistence;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Record;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

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

    SOURCE_CONNECTION_IMPLEMENTATION = new SourceConnectionImplementation();
    SOURCE_CONNECTION_IMPLEMENTATION.setWorkspaceId(workspaceId);
    SOURCE_CONNECTION_IMPLEMENTATION.setSourceSpecificationId(sourceSpecificationId);
    SOURCE_CONNECTION_IMPLEMENTATION.setSourceImplementationId(sourceImplementationId);
    SOURCE_CONNECTION_IMPLEMENTATION.setConfiguration(implementationJson);
    SOURCE_CONNECTION_IMPLEMENTATION.setTombstone(false);

    final UUID destinationImplementationId = UUID.randomUUID();
    final UUID destinationSpecificationId = Integrations.POSTGRES_TARGET.getSpecId();

    DESTINATION_CONNECTION_IMPLEMENTATION = new DestinationConnectionImplementation();
    DESTINATION_CONNECTION_IMPLEMENTATION.setWorkspaceId(workspaceId);
    DESTINATION_CONNECTION_IMPLEMENTATION.setDestinationSpecificationId(destinationSpecificationId);
    DESTINATION_CONNECTION_IMPLEMENTATION.setDestinationImplementationId(destinationImplementationId);
    DESTINATION_CONNECTION_IMPLEMENTATION.setConfiguration(implementationJson);

    final Column column = new Column();
    column.setDataType(DataType.STRING);
    column.setName("id");
    column.setSelected(true);

    final Table table = new Table();
    table.setName("users");
    table.setColumns(Lists.newArrayList(column));
    table.setSelected(true);

    final Schema schema = new Schema();
    schema.setTables(Lists.newArrayList(table));

    final UUID connectionId = UUID.randomUUID();

    STANDARD_SYNC = new StandardSync();
    STANDARD_SYNC.setConnectionId(connectionId);
    STANDARD_SYNC.setName("presto to hudi");
    STANDARD_SYNC.setStatus(StandardSync.Status.ACTIVE);
    STANDARD_SYNC.setSchema(schema);
    STANDARD_SYNC.setSourceImplementationId(sourceImplementationId);
    STANDARD_SYNC.setDestinationImplementationId(destinationImplementationId);
    STANDARD_SYNC.setSyncMode(StandardSync.SyncMode.APPEND);

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

  @BeforeEach
  public void setup() throws SQLException {
    // todo (cgardens) - truncate whole db.
    DatabaseHelper.query(connectionPool, ctx -> ctx.execute("DELETE FROM jobs"));

    // noinspection unchecked
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
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig();
    jobCheckConnectionConfig.setConnectionConfiguration(SOURCE_CONNECTION_IMPLEMENTATION.getConfiguration());
    jobCheckConnectionConfig.setDockerImage(imageName);

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setConfigType(JobConfig.ConfigType.CHECK_CONNECTION_SOURCE);
    jobConfig.setCheckConnection(jobCheckConnectionConfig);

    assertJobConfigEqualJobDbRecord(jobId, SOURCE_CONNECTION_IMPLEMENTATION.getSourceImplementationId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testCreateDestinationCheckConnectionJob() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createDestinationCheckConnectionJob(DESTINATION_CONNECTION_IMPLEMENTATION);

    final Record jobEntry = getJobRecord(jobId);

    final String imageName =
        Integrations.findBySpecId(DESTINATION_CONNECTION_IMPLEMENTATION.getDestinationSpecificationId()).getDiscoverSchemaImage();
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig();
    jobCheckConnectionConfig.setConnectionConfiguration(DESTINATION_CONNECTION_IMPLEMENTATION.getConfiguration());
    jobCheckConnectionConfig.setDockerImage(imageName);

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setConfigType(JobConfig.ConfigType.CHECK_CONNECTION_DESTINATION);
    jobConfig.setCheckConnection(jobCheckConnectionConfig);

    assertJobConfigEqualJobDbRecord(jobId, DESTINATION_CONNECTION_IMPLEMENTATION.getDestinationImplementationId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testCreateDiscoverSchemaJob() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createDiscoverSchemaJob(SOURCE_CONNECTION_IMPLEMENTATION);

    final Record jobEntry = getJobRecord(jobId);

    final String imageName = Integrations.findBySpecId(SOURCE_CONNECTION_IMPLEMENTATION.getSourceSpecificationId()).getDiscoverSchemaImage();
    final JobDiscoverSchemaConfig jobDiscoverSchemaConfig = new JobDiscoverSchemaConfig();
    jobDiscoverSchemaConfig.setConnectionConfiguration(SOURCE_CONNECTION_IMPLEMENTATION.getConfiguration());
    jobDiscoverSchemaConfig.setDockerImage(imageName);

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setConfigType(JobConfig.ConfigType.DISCOVER_SCHEMA);
    jobConfig.setDiscoverSchema(jobDiscoverSchemaConfig);

    assertJobConfigEqualJobDbRecord(jobId, SOURCE_CONNECTION_IMPLEMENTATION.getSourceImplementationId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testCreateSyncJob() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createSyncJob(SOURCE_CONNECTION_IMPLEMENTATION, DESTINATION_CONNECTION_IMPLEMENTATION, STANDARD_SYNC);

    final Record jobEntry = getJobRecord(jobId);

    final String sourceImageName = Integrations.findBySpecId(SOURCE_CONNECTION_IMPLEMENTATION.getSourceSpecificationId()).getSyncImage();
    final String destinationImageName =
        Integrations.findBySpecId(DESTINATION_CONNECTION_IMPLEMENTATION.getDestinationSpecificationId()).getSyncImage();
    final JobSyncConfig jobSyncConfig = new JobSyncConfig();
    jobSyncConfig.setSourceConnectionImplementation(SOURCE_CONNECTION_IMPLEMENTATION);
    jobSyncConfig.setSourceDockerImage(sourceImageName);
    jobSyncConfig.setDestinationConnectionImplementation(DESTINATION_CONNECTION_IMPLEMENTATION);
    jobSyncConfig.setDestinationDockerImage(destinationImageName);
    jobSyncConfig.setStandardSync(STANDARD_SYNC);

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setConfigType(JobConfig.ConfigType.SYNC);
    jobConfig.setSync(jobSyncConfig);

    assertJobConfigEqualJobDbRecord(jobId, STANDARD_SYNC.getConnectionId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testGetJob() throws IOException {
    final long jobId = schedulerPersistence.createSourceCheckConnectionJob(SOURCE_CONNECTION_IMPLEMENTATION);

    final Job actual = schedulerPersistence.getJob(jobId);

    final Job expected = getExpectedJob(jobId);

    assertEquals(expected, actual);
  }

  @Test
  public void testListJobs() throws IOException {
    final long jobId = schedulerPersistence.createSourceCheckConnectionJob(SOURCE_CONNECTION_IMPLEMENTATION);

    final List<Job> actualList = schedulerPersistence
        .listJobs(JobConfig.ConfigType.CHECK_CONNECTION_SOURCE, SOURCE_CONNECTION_IMPLEMENTATION.getSourceImplementationId().toString());

    final Job actual = actualList.get(0);
    final Job expected = getExpectedJob(jobId);

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
    final JobSyncConfig jobSyncConfig = new JobSyncConfig();
    jobSyncConfig.setSourceConnectionImplementation(SOURCE_CONNECTION_IMPLEMENTATION);
    jobSyncConfig.setSourceDockerImage(sourceImageName);
    jobSyncConfig.setDestinationConnectionImplementation(DESTINATION_CONNECTION_IMPLEMENTATION);
    jobSyncConfig.setDestinationDockerImage(destinationImageName);
    jobSyncConfig.setStandardSync(STANDARD_SYNC);

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setConfigType(JobConfig.ConfigType.SYNC);
    jobConfig.setSync(jobSyncConfig);

    final String scope = ScopeHelper.createScope(JobConfig.ConfigType.SYNC, STANDARD_SYNC.getConnectionId().toString());

    final Job expected = new Job(
        jobId,
        scope,
        JobStatus.PENDING,
        jobConfig,
        null,
        JobLogs.getLogDirectory(scope),
        JobLogs.getLogDirectory(scope),
        afterNow.getEpochSecond(),
        null,
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
  public void testGetJobFromRecord() throws IOException, SQLException {
    final long jobId = schedulerPersistence.createSourceCheckConnectionJob(SOURCE_CONNECTION_IMPLEMENTATION);
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
    final String imageName = Integrations.findBySpecId(SOURCE_CONNECTION_IMPLEMENTATION.getSourceSpecificationId()).getDiscoverSchemaImage();
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig();
    jobCheckConnectionConfig.setConnectionConfiguration(SOURCE_CONNECTION_IMPLEMENTATION.getConfiguration());
    jobCheckConnectionConfig.setDockerImage(imageName);

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setConfigType(JobConfig.ConfigType.CHECK_CONNECTION_SOURCE);
    jobConfig.setCheckConnection(jobCheckConnectionConfig);

    final String scope =
        ScopeHelper.createScope(JobConfig.ConfigType.CHECK_CONNECTION_SOURCE,
            SOURCE_CONNECTION_IMPLEMENTATION.getSourceImplementationId().toString());

    return new Job(
        jobId,
        scope,
        JobStatus.PENDING,
        jobConfig,
        null,
        JobLogs.getLogDirectory(scope),
        JobLogs.getLogDirectory(scope),
        NOW.getEpochSecond(),
        null,
        NOW.getEpochSecond());
  }

}
