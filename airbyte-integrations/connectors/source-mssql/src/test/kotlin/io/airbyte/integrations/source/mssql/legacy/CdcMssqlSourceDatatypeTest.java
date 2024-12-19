/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mssql.legacy;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.Database;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.BaseImage;
import io.airbyte.integrations.source.mssql.MsSQLTestDatabase.ContainerModifier;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import org.junit.jupiter.api.TestInstance;
import org.junit.jupiter.api.TestInstance.Lifecycle;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;

@TestInstance(Lifecycle.PER_METHOD)
@Execution(ExecutionMode.CONCURRENT)
public class CdcMssqlSourceDatatypeTest extends AbstractMssqlSourceDatatypeTest {

  private final ExecutorService executor = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withCdcReplication()
        .withoutSsl()
        .build();
  }

  @Override
  protected Database setupDatabase() {
    testdb = MsSQLTestDatabase.in(BaseImage.MSSQL_2022, ContainerModifier.AGENT)
        .withCdc();
    return testdb.getDatabase();
  }

  protected void createTables() throws Exception {
    List<Callable<MsSQLTestDatabase>> createTableTasks = new ArrayList<>();
    List<Callable<MsSQLTestDatabase>> enableCdcForTableTasks = new ArrayList<>();
    for (var test : testDataHolders) {
      createTableTasks.add(() -> testdb.with(test.getCreateSqlQuery()));
      enableCdcForTableTasks.add(() -> testdb.withCdcForTable(test.getNameSpace(), test.getNameWithTestPrefix(), null));
    }
    executor.invokeAll(createTableTasks);
    executor.invokeAll(enableCdcForTableTasks);
  }

  protected void populateTables() throws Exception {
    List<Callable<MsSQLTestDatabase>> insertTasks = new ArrayList<>();
    List<Callable<MsSQLTestDatabase>> waitForCdcRecordsTasks = new ArrayList<>();
    for (var test : testDataHolders) {
      insertTasks.add(() -> {
        this.database.query((ctx) -> {
          List<String> sql = test.getInsertSqlQueries();
          Objects.requireNonNull(ctx);
          sql.forEach(ctx::fetch);
          return null;
        });
        return null;
      });
      waitForCdcRecordsTasks.add(() -> testdb.waitForCdcRecords(test.getNameSpace(), test.getNameWithTestPrefix(), test.getExpectedValues().size()));
    }
    // executor.invokeAll(insertTasks);
    executor.invokeAll(insertTasks);
    executor.invokeAll(waitForCdcRecordsTasks);
  }

  @Override
  public boolean testCatalog() {
    return true;
  }

}
