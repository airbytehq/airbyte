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

package io.dataline.workers.singer;

import static org.junit.jupiter.api.Assertions.assertEquals;

import io.dataline.config.JobSyncConfig;
import io.dataline.config.JobSyncOutput;
import io.dataline.db.DatabaseHelper;
import io.dataline.workers.BaseWorkerTestCase;
import io.dataline.workers.JobStatus;
import io.dataline.workers.OutputAndStatus;
import io.dataline.workers.PostgreSQLContainerTestHelper;
import java.io.IOException;
import java.sql.SQLException;
import java.util.HashSet;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.Condition;
import org.jooq.Field;
import org.jooq.Record;
import org.jooq.Result;
import org.junit.Before;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestInstance;
import org.testcontainers.containers.PostgreSQLContainer;
import org.testcontainers.utility.MountableFile;

// TODO this test currently only tests PSQL. Will be refactored with the addition of new
// integrations.
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
public final class SingerSyncWorkerTest extends BaseWorkerTestCase {

  PostgreSQLContainer sourceDb;
  PostgreSQLContainer targetDb;

  @BeforeAll
  public void initDb() {
    sourceDb = new PostgreSQLContainer();
    sourceDb.start();
    targetDb = new PostgreSQLContainer();
    targetDb.start();
  }

  @Before
  public void wipeDb() throws SQLException {
    PostgreSQLContainerTestHelper.wipePublicSchema(sourceDb);
    PostgreSQLContainerTestHelper.wipePublicSchema(targetDb);
  }

  @Test
  public void testFirstTimeFullTableSync() throws IOException, SQLException, InterruptedException {
    PostgreSQLContainerTestHelper.runSqlScript(
        MountableFile.forClasspathResource("simple_postgres_init.sql"), sourceDb);
    String tapConfig = PostgreSQLContainerTestHelper.getSingerTapConfig(sourceDb);
    String targetConfig = PostgreSQLContainerTestHelper.getSingerTargetConfig(targetDb);

    OutputAndStatus<JobSyncOutput> syncOutputAndStatus =
        new SingerSyncWorker(
                SingerTap.POSTGRES,
                tapConfig,
                readResource("simple_postgres_full_table_sync_catalog.json"),
                "{}", // full table sync, no state needed
                SingerTarget.POSTGRES,
                targetConfig)
            .run(null, workspaceDirectory);

    assertEquals(JobStatus.SUCCESSFUL, syncOutputAndStatus.getStatus());
    JobSyncOutput jobSyncOutput = syncOutputAndStatus.getOutput().get();
    assertEquals(5, jobSyncOutput.getStandardSyncSummary().getRecordsSynced());

    BasicDataSource sourceDbPool =
        DatabaseHelper.getConnectionPool(
            sourceDb.getUsername(), sourceDb.getPassword(), sourceDb.getJdbcUrl());
    BasicDataSource targetDbPool =
        DatabaseHelper.getConnectionPool(
            targetDb.getUsername(), targetDb.getPassword(), targetDb.getJdbcUrl());

    Set<String> sourceTables = listTables(sourceDbPool);
    Set<String> targetTables = listTables(targetDbPool);
    assertEquals(sourceTables, targetTables);

    // TODO validate that indices are synced? what defines
    for (String table : sourceTables) {
      assertTablesEquivalent(sourceDbPool, targetDbPool, table);
    }
  }

  @Test
  public void testIncrementalSyncs() {
    // TODO
  }

  private void assertTablesEquivalent(
      BasicDataSource sourceDbPool, BasicDataSource targetDbPool, String table)
      throws SQLException {
    long sourceTableCount = getTableCount(sourceDbPool, table);
    long targetTableCount = getTableCount(targetDbPool, table);
    assertEquals(sourceTableCount, targetTableCount);
    Result<Record> allRecords =
        DatabaseHelper.query(
            sourceDbPool, context -> context.fetch(String.format("SELECT * FROM %s;", table)));
    for (Record sourceTableRecord : allRecords) {
      assertRecordInTable(sourceTableRecord, targetDbPool, table);
    }
  }

  /**
   * Verifies that a record in the target table and database exists with the same (and potentially
   * more) fields.
   */
  private void assertRecordInTable(Record record, BasicDataSource connectionPool, String tableName)
      throws SQLException {

    Set<Condition> conditions = new HashSet<>();
    for (Field<?> field : record.fields()) {
      Object fieldValue = record.get(field);
      Condition eq = ((Field) field).equal(fieldValue);
      conditions.add(eq);
    }

    Result<Record> presentRecords =
        DatabaseHelper.query(
            connectionPool, context -> context.select().from(tableName).where(conditions).fetch());

    // TODO validate that the correct number of records exists? currently if the same record exists
    //  multiple times in the source but once in destination, this returns true.
    assertEquals(1, presentRecords.size());
  }

  private Set<String> listTables(BasicDataSource connectionPool) throws SQLException {
    return DatabaseHelper.query(
        connectionPool,
        context -> {
          Result<Record> fetch =
              context.fetch(
                  "SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'");
          return fetch.stream()
              .map(record -> (String) record.get("tablename"))
              .collect(Collectors.toSet());
        });
  }

  private long getTableCount(BasicDataSource connectionPool, String tableName) throws SQLException {
    return DatabaseHelper.query(
        connectionPool,
        context -> {
          Result<Record> record =
              context.fetch(String.format("SELECT COUNT(*) FROM %s;", tableName));
          return (long) record.stream().findFirst().get().get(0);
        });
  }
}
