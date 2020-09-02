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

class DefaultSchedulerPersistenceTest {

  @SuppressWarnings("rawtypes")
  private static PostgreSQLContainer container;
  private static BasicDataSource connectionPool;

  private static final SourceConnectionImplementation sourceConnectionImplementation;
  private static final DestinationConnectionImplementation destinationConnectionImplementation;
  private static final StandardSync standardSync;
  private static final Instant now;

  static {
    final UUID workspaceId = UUID.randomUUID();
    final UUID sourceImplementationId = UUID.randomUUID();
    final UUID sourceSpecificationId = Integrations.POSTGRES_TAP.getSpecId();

    JsonNode implementationJson = Jsons.jsonNode(ImmutableMap.builder()
        .put("apiKey", "123-abc")
        .put("hostname", "dataline.io")
        .build());

    sourceConnectionImplementation = new SourceConnectionImplementation();
    sourceConnectionImplementation.setWorkspaceId(workspaceId);
    sourceConnectionImplementation.setSourceSpecificationId(sourceSpecificationId);
    sourceConnectionImplementation.setSourceImplementationId(sourceImplementationId);
    sourceConnectionImplementation.setConfiguration(implementationJson);
    sourceConnectionImplementation.setTombstone(false);

    final UUID destinationImplementationId = UUID.randomUUID();
    final UUID destinationSpecificationId = Integrations.POSTGRES_TARGET.getSpecId();

    destinationConnectionImplementation = new DestinationConnectionImplementation();
    destinationConnectionImplementation.setWorkspaceId(workspaceId);
    destinationConnectionImplementation.setDestinationSpecificationId(destinationSpecificationId);
    destinationConnectionImplementation.setDestinationImplementationId(destinationImplementationId);
    destinationConnectionImplementation.setConfiguration(implementationJson);

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

    standardSync = new StandardSync();
    standardSync.setConnectionId(connectionId);
    standardSync.setName("presto to hudi");
    standardSync.setStatus(StandardSync.Status.ACTIVE);
    standardSync.setSchema(schema);
    standardSync.setSourceImplementationId(sourceImplementationId);
    standardSync.setDestinationImplementationId(UUID.randomUUID());
    standardSync.setSyncMode(StandardSync.SyncMode.APPEND);

    now = Instant.now();
    @SuppressWarnings("unchecked")
    Supplier<Instant> timeSupplier = mock(Supplier.class);
    when(timeSupplier.get()).thenReturn(now);

  }

  @SuppressWarnings("rawtypes")
  @BeforeAll
  public static void dbSetup() {
    container = new PostgreSQLContainer("postgres:13-alpine")
        .withDatabaseName("dataline")
        .withUsername("docker")
        .withPassword("docker");
    container.start();

    try {
      container.copyFileToContainer(MountableFile.forClasspathResource("schema.sql"), "/etc/init.sql");
      // execInContainer uses Docker's EXEC so it needs to be split up like this
      container.execInContainer(
          "psql", "-d", "dataline", "-U", "docker", "-a", "-f", "/etc/init.sql");

    } catch (InterruptedException | IOException e) {
      throw new RuntimeException(e);
    }

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
    DatabaseHelper.query(connectionPool, ctx -> ctx.truncate("jobs"));

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
    final SchedulerPersistence schedulerPersistence = new DefaultSchedulerPersistence(connectionPool);
    final long jobId = schedulerPersistence.createSourceCheckConnectionJob(sourceConnectionImplementation);

    Record jobEntry = getJobRecord(jobId);

    final String imageName = Integrations.findBySpecId(sourceConnectionImplementation.getSourceSpecificationId()).getDiscoverSchemaImage();
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig();
    jobCheckConnectionConfig.setConnectionConfiguration(sourceConnectionImplementation.getConfiguration());
    jobCheckConnectionConfig.setDockerImage(imageName);

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setConfigType(JobConfig.ConfigType.CHECK_CONNECTION_SOURCE);
    jobConfig.setCheckConnection(jobCheckConnectionConfig);

    assertJobConfigEqualJobDbRecord(jobId, sourceConnectionImplementation.getSourceImplementationId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testCreateDestinationCheckConnectionJob() throws IOException, SQLException {
    final SchedulerPersistence schedulerPersistence = new DefaultSchedulerPersistence(connectionPool);
    final long jobId = schedulerPersistence.createDestinationCheckConnectionJob(destinationConnectionImplementation);

    Record jobEntry = getJobRecord(jobId);

    final String imageName = Integrations.findBySpecId(destinationConnectionImplementation.getDestinationSpecificationId()).getDiscoverSchemaImage();
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig();
    jobCheckConnectionConfig.setConnectionConfiguration(destinationConnectionImplementation.getConfiguration());
    jobCheckConnectionConfig.setDockerImage(imageName);

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setConfigType(JobConfig.ConfigType.CHECK_CONNECTION_DESTINATION);
    jobConfig.setCheckConnection(jobCheckConnectionConfig);

    assertJobConfigEqualJobDbRecord(jobId, destinationConnectionImplementation.getDestinationImplementationId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testCreateDiscoverSchemaJob() throws IOException, SQLException {
    final SchedulerPersistence schedulerPersistence = new DefaultSchedulerPersistence(connectionPool);
    final long jobId = schedulerPersistence.createDiscoverSchemaJob(sourceConnectionImplementation);

    Record jobEntry = getJobRecord(jobId);

    final String imageName = Integrations.findBySpecId(sourceConnectionImplementation.getSourceSpecificationId()).getDiscoverSchemaImage();
    final JobDiscoverSchemaConfig jobDiscoverSchemaConfig = new JobDiscoverSchemaConfig();
    jobDiscoverSchemaConfig.setConnectionConfiguration(sourceConnectionImplementation.getConfiguration());
    jobDiscoverSchemaConfig.setDockerImage(imageName);

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setConfigType(JobConfig.ConfigType.DISCOVER_SCHEMA);
    jobConfig.setDiscoverSchema(jobDiscoverSchemaConfig);

    assertJobConfigEqualJobDbRecord(jobId, sourceConnectionImplementation.getSourceImplementationId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testCreateSyncJob() throws IOException, SQLException {
    final SchedulerPersistence schedulerPersistence = new DefaultSchedulerPersistence(connectionPool);
    final long jobId = schedulerPersistence.createSyncJob(sourceConnectionImplementation, destinationConnectionImplementation, standardSync);

    Record jobEntry = getJobRecord(jobId);

    final String sourceImageName = Integrations.findBySpecId(sourceConnectionImplementation.getSourceSpecificationId()).getSyncImage();
    final String destinationImageName = Integrations.findBySpecId(destinationConnectionImplementation.getDestinationSpecificationId()).getSyncImage();
    final JobSyncConfig jobSyncConfig = new JobSyncConfig();
    jobSyncConfig.setSourceConnectionImplementation(sourceConnectionImplementation);
    jobSyncConfig.setSourceDockerImage(sourceImageName);
    jobSyncConfig.setDestinationConnectionImplementation(destinationConnectionImplementation);
    jobSyncConfig.setDestinationDockerImage(destinationImageName);
    jobSyncConfig.setStandardSync(standardSync);

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setConfigType(JobConfig.ConfigType.SYNC);
    jobConfig.setSync(jobSyncConfig);

    assertJobConfigEqualJobDbRecord(jobId, standardSync.getConnectionId().toString(), jobConfig, jobEntry);
  }

  @Test
  public void testGetJob() throws IOException {
    final SchedulerPersistence schedulerPersistence = new DefaultSchedulerPersistence(connectionPool);
    final long jobId = schedulerPersistence.createSourceCheckConnectionJob(sourceConnectionImplementation);

    final Job actual = schedulerPersistence.getJob(jobId);

    final Job expected = getExpectedJob(jobId);

    assertEquals(expected, actual);
  }

  @Test
  public void testListJobs() throws IOException {
    final SchedulerPersistence schedulerPersistence = new DefaultSchedulerPersistence(connectionPool);
    final long jobId = schedulerPersistence.createSourceCheckConnectionJob(sourceConnectionImplementation);

    final List<Job> actualList = schedulerPersistence
        .listJobs(JobConfig.ConfigType.CHECK_CONNECTION_SOURCE, sourceConnectionImplementation.getSourceImplementationId().toString());

    assertEquals(1, actualList.size());
    final Job actual = actualList.get(0);
    final Job expected = getExpectedJob(jobId);

    assertEquals(expected, actual);

  }

  @Test
  public void testGetJobFromRecord() throws IOException, SQLException {
    final SchedulerPersistence schedulerPersistence = new DefaultSchedulerPersistence(connectionPool);
    final long jobId = schedulerPersistence.createSourceCheckConnectionJob(sourceConnectionImplementation);
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
    assertEquals(now.getEpochSecond(), actual.getValue("created_at", LocalDateTime.class).toEpochSecond(ZoneOffset.UTC));
    assertNull(actual.getValue("started_at", LocalDateTime.class));
    assertEquals(now.getEpochSecond(), actual.getValue("updated_at", LocalDateTime.class).toEpochSecond(ZoneOffset.UTC));
    assertNull(actual.get("output"));
    assertEquals(expected, Jsons.deserialize(actual.get("config", String.class), JobConfig.class));
  }

  private Job getExpectedJob(long jobId) {
    final String imageName = Integrations.findBySpecId(sourceConnectionImplementation.getSourceSpecificationId()).getDiscoverSchemaImage();
    final JobCheckConnectionConfig jobCheckConnectionConfig = new JobCheckConnectionConfig();
    jobCheckConnectionConfig.setConnectionConfiguration(sourceConnectionImplementation.getConfiguration());
    jobCheckConnectionConfig.setDockerImage(imageName);

    final JobConfig jobConfig = new JobConfig();
    jobConfig.setConfigType(JobConfig.ConfigType.CHECK_CONNECTION_SOURCE);
    jobConfig.setCheckConnection(jobCheckConnectionConfig);

    final String scope =
        ScopeHelper.createScope(JobConfig.ConfigType.CHECK_CONNECTION_SOURCE, sourceConnectionImplementation.getSourceImplementationId().toString());

    return new Job(
        jobId,
        scope,
        JobStatus.PENDING,
        jobConfig,
        null,
        JobLogs.getLogDirectory(scope),
        JobLogs.getLogDirectory(scope),
        now.getEpochSecond(),
        null,
        now.getEpochSecond());
  }

}
