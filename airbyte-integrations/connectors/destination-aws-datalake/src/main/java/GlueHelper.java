/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.aws_datalake;

import java.util.ArrayList;
import java.util.Iterator;
import java.util.List;
import software.amazon.awssdk.auth.credentials.AwsCredentials;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.glue.GlueClient;
import software.amazon.awssdk.services.glue.model.BatchDeleteTableRequest;
import software.amazon.awssdk.services.glue.model.GetTablesRequest;
import software.amazon.awssdk.services.glue.model.GetTablesResponse;
import software.amazon.awssdk.services.glue.model.Table;
import software.amazon.awssdk.services.glue.paginators.GetTablesIterable;

public class GlueHelper {

  private AwsCredentials awsCredentials;
  private Region region;
  private GlueClient glueClient;

  public GlueHelper(AwsCredentials credentials, Region region) {
    this.awsCredentials = credentials;
    this.region = region;

    var credProvider = StaticCredentialsProvider.create(credentials);
    this.glueClient = GlueClient.builder().region(region).credentialsProvider(credProvider).build();
  }

  private GetTablesIterable getAllTables(String DatabaseName) {

    GetTablesRequest getTablesRequest = GetTablesRequest.builder().databaseName(DatabaseName).build();
    GetTablesIterable getTablesPaginator = glueClient.getTablesPaginator(getTablesRequest);

    return getTablesPaginator;
  }

  private BatchDeleteTableRequest getBatchDeleteRequest(String databaseName, GetTablesIterable getTablesPaginator) {
    List<String> tablesToDelete = new ArrayList<String>();
    for (GetTablesResponse response : getTablesPaginator) {
      List<Table> tablePage = response.tableList();
      Iterator<Table> tableIterator = tablePage.iterator();
      while (tableIterator.hasNext()) {
        Table table = tableIterator.next();
        tablesToDelete.add(table.name());
      }
    }
    BatchDeleteTableRequest batchDeleteRequest = BatchDeleteTableRequest.builder().databaseName(databaseName).tablesToDelete(tablesToDelete).build();
    return batchDeleteRequest;
  }

  public void purgeDatabase(String databaseName) {
    int countRetries = 0;
    while (countRetries < 5) {
      try {
        GetTablesIterable allTables = getAllTables(databaseName);
        BatchDeleteTableRequest batchDeleteTableRequest = getBatchDeleteRequest(databaseName, allTables);
        glueClient.batchDeleteTable(batchDeleteTableRequest);
        return;
      } catch (Exception e) {
        countRetries++;
      }
    }
  }

}
