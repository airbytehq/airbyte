/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_glue;

import com.amazonaws.services.glue.AWSGlue;
import com.amazonaws.services.glue.model.BatchDeleteTableRequest;
import com.amazonaws.services.glue.model.GetTablesRequest;
import com.amazonaws.services.glue.model.GetTablesResult;
import com.amazonaws.services.glue.model.Table;
import java.io.Closeable;
import java.util.ArrayList;
import java.util.List;

public class GlueTestClient implements Closeable {

  private final AWSGlue glueClient;

  public GlueTestClient(AWSGlue glueClient) {
    this.glueClient = glueClient;
  }

  private List<Table> getAllTables(String databaseName) {

    List<Table> tables = new ArrayList<>();
    String nextToken = null;
    do {
      GetTablesRequest getTablesRequest =
          new GetTablesRequest().withDatabaseName(databaseName).withNextToken(nextToken);

      GetTablesResult getTablesResult = glueClient.getTables(getTablesRequest);
      tables.addAll(getTablesResult.getTableList());

      nextToken = getTablesResult.getNextToken();

    } while (nextToken != null);

    return tables;

  }

  private BatchDeleteTableRequest getBatchDeleteRequest(String databaseName, List<Table> tables) {
    List<String> tablesToDelete = tables.stream().map(Table::getName).toList();
    return new BatchDeleteTableRequest()
        .withDatabaseName(databaseName)
        .withTablesToDelete(tablesToDelete);
  }

  public void purgeDatabase(String databaseName) {
    int countRetries = 0;
    while (countRetries < 5) {
      try {
        List<Table> allTables = getAllTables(databaseName);
        BatchDeleteTableRequest batchDeleteTableRequest = getBatchDeleteRequest(databaseName, allTables);
        glueClient.batchDeleteTable(batchDeleteTableRequest);
        return;
      } catch (Exception e) {
        countRetries++;
      }
    }
  }

  @Override
  public void close() {
    glueClient.shutdown();
  }

}
