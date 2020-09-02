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

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.google.common.collect.Lists;
import io.dataline.commons.json.Jsons;
import io.dataline.config.Column;
import io.dataline.config.DataType;
import io.dataline.config.DestinationConnectionImplementation;
import io.dataline.config.JobConfig;
import io.dataline.config.Schema;
import io.dataline.config.SourceConnectionImplementation;
import io.dataline.config.StandardSync;
import io.dataline.config.Table;
import io.dataline.db.DatabaseHelper;
import io.dataline.integrations.Integrations;
import java.io.IOException;
import java.sql.SQLException;
import java.time.LocalDateTime;
import java.time.ZoneOffset;
import java.util.UUID;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Record;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

class DefaultSchedulerPersistenceTest {

  private static PostgreSQLContainer container;
  private static BasicDataSource connectionPool;

  private static SourceConnectionImplementation sourceConnectionImplementation;
  private static DestinationConnectionImplementation destinationConnectionImplementation;
  private static StandardSync standardSync;

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

  }

  @BeforeAll
  public static void dbSetup() {
    container =
        new PostgreSQLContainer("postgres:13-alpine")
            .withDatabaseName("dataline")
            .withUsername("docker")
            .withPassword("docker");;
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

  @Test
  public void test() throws IOException {
    final SchedulerPersistence schedulerPersistence = new DefaultSchedulerPersistence(connectionPool);
    final long jobId = schedulerPersistence.createSyncJob(sourceConnectionImplementation, destinationConnectionImplementation, standardSync);

    Record jobEntry;
    try {
      jobEntry = DatabaseHelper.query(
          connectionPool,
          ctx -> ctx.fetch("SELECT * FROM jobs WHERE id = ?", jobId).stream()
              .findFirst()
              .orElseThrow(
                  () -> new RuntimeException("Could not find job with id: " + jobId)));
    } catch (SQLException e) {
      throw new IOException(e);
    }

    final String scope = ScopeHelper.createScope(JobConfig.ConfigType.SYNC, standardSync.getConnectionId().toString());
    assertEquals(jobId, jobEntry.get("id"));
    assertEquals(scope, jobEntry.get("scope"));
    assertEquals("pending", jobEntry.get("status", String.class));
    assertEquals("logs/jobs/" + scope, jobEntry.get("stdout_path", String.class));
    assertEquals("logs/jobs/" + scope, jobEntry.get("stderr_path", String.class));
    assertTrue(1 < jobEntry.getValue("created_at", LocalDateTime.class).toEpochSecond(ZoneOffset.UTC));
    assertNull(jobEntry.getValue("started_at", LocalDateTime.class));
    assertTrue(1 < jobEntry.getValue("updated_at", LocalDateTime.class).toEpochSecond(ZoneOffset.UTC));
  }

}
