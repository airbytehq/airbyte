/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.clickhouse;

import com.clickhouse.client.ClickHouseFormat;
import com.clickhouse.jdbc.ClickHouseConnection;
import com.clickhouse.jdbc.ClickHouseStatement;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.integrations.base.JavaBaseConstants;
import io.airbyte.integrations.destination.jdbc.JdbcSqlOperations;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.apache.commons.text.StringSubstitutor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class ClickhouseSqlOperations extends JdbcSqlOperations {

  private static final Logger LOGGER = LoggerFactory.getLogger(ClickhouseSqlOperations.class);
  private ClickhouseDestinationConfig config;

  public void setConfig(final ClickhouseDestinationConfig config) {
    this.config = config;
  }

  @Override
  public void createSchemaIfNotExists(final JdbcDatabase database, final String schemaName) throws Exception {
    StringBuilder query = new StringBuilder("CREATE DATABASE IF NOT EXISTS ${schema}");
    if (config.deploy_config().type().equals("self-hosted-cluster")) {
      query.append(" ON CLUSTER ${cluster}");
    }
    query.append(";\n");

    Map<String, String> params = new HashMap<String, String>();
    params.put("schema", schemaName);
    params.put("cluster", config.deploy_config().cluster());

    database.execute(StringSubstitutor.replace(query, params));
  }

  @Override
  public boolean isSchemaRequired() {
    return false;
  }

  @Override
  public String createTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    StringBuilder query = new StringBuilder("CREATE TABLE IF NOT EXISTS ${schema}.${table}");

    // On self-hosted, if clustering is enabled, change the table name to x_mat to
    // indicate this is the materialized set of tables. Later on, we'll create the
    // Distributed virtual tables with name x on top of these materialized tables.
    // On Clickhouse Cloud, there is automatic sharding and replication so we don't
    // need to do this.
    if (config.deploy_config().type().equals("self-hosted-cluster")) {
      query.append("_mat ON CLUSTER ${cluster}");
    }

    query.append(" ( \n"
        + "${col_name_ab_id} String,\n"
        + "${col_name_data} String,\n"
        + "${col_name_emitted_at} DateTime64(3, 'GMT') DEFAULT now(),\n"
        + "PRIMARY KEY(${col_name_ab_id})\n"
        + ")\n"
        + "ENGINE = ");

    if (config.deploy_config().replication()) {
      query.append("Replicated");
    }
    query.append("${engine}(");
    // If we have a self hosted cluster, we need to add additional Keeper parameters
    if (config.deploy_config().type().equals("self-hosted-cluster")) {
      query.append("'/clickhouse/tables/{shard}/{database}/{table}', '{replica}'");
    }
    query.append(");\n");

    // On a self-hosted cluster, we now create the Distributed virtual table,
    // sharding on a hashed Airbyte record ID
    if (config.deploy_config().type().equals("self-hosted-cluster")) {
      query.append(
          "CREATE TABLE IF NOT EXISTS ${schema}.${table} ON CLUSTER ${cluster} AS ${schema}.${table}_mat ENGINE = Distributed(${cluster}, ${schema}, ${table}_mat, cityHash64(${col_name_ab_id}));\n");
    }

    Map<String, String> params = new HashMap<String, String>();
    params.put("schema", schemaName);
    params.put("table", tableName);
    params.put("cluster", config.deploy_config().cluster());
    params.put("engine", config.engine());
    params.put("col_name_ab_id", JavaBaseConstants.COLUMN_NAME_AB_ID);
    params.put("col_name_data", JavaBaseConstants.COLUMN_NAME_DATA);
    params.put("col_name_emitted_at", JavaBaseConstants.COLUMN_NAME_EMITTED_AT);

    return StringSubstitutor.replace(query, params);
  }

  @Override
  public void dropTableIfExists(final JdbcDatabase database, final String schemaName, final String tableName)
      throws SQLException {
    StringBuilder query = new StringBuilder("DROP TABLE IF EXISTS ${schema}.${table}");

    if (config.deploy_config().type().equals("self-hosted-cluster")) {
      query.append(" ON CLUSTER ${cluster};\n");
      query.append("DROP TABLE IF EXISTS ${schema}.${table}_mat ON CLUSTER ${cluster}");
    }
    query.append(";\n");

    Map<String, String> params = new HashMap<String, String>();
    params.put("schema", schemaName);
    params.put("table", tableName);
    params.put("cluster", config.deploy_config().cluster());

    String formattedQuery = StringSubstitutor.replace(query, params);

    try {
      database.execute(formattedQuery);
    } catch (SQLException e) {
      throw checkForKnownConfigExceptions(e).orElseThrow(() -> e);
    }
  }

  @Override
  public String truncateTableQuery(final JdbcDatabase database, final String schemaName, final String tableName) {
    StringBuilder query = new StringBuilder("TRUNCATE TABLE ${schema}.${table}");
    if (config.deploy_config().type().equals("self-hosted-cluster")) {
      query.append(" ON CLUSTER ${cluster}");
    }
    query.append(";\n");

    Map<String, String> params = new HashMap<String, String>();
    params.put("schema", schemaName);
    params.put("table", tableName);
    params.put("cluster", config.deploy_config().cluster());

    return StringSubstitutor.replace(query, params);
  }

  @Override
  public void executeTransaction(final JdbcDatabase database, final List<String> queries) throws Exception {
    // Note: ClickHouse does not support multi query
    for (final String query : queries) {
      database.execute(query);
    }
  }

  @Override
  public void insertRecordsInternal(final JdbcDatabase database,
                                    final List<AirbyteRecordMessage> records,
                                    final String schemaName,
                                    final String tmpTableName)
      throws SQLException {
    LOGGER.info("actual size of batch: {}", records.size());

    if (records.isEmpty()) {
      return;
    }

    database.execute(connection -> {
      File tmpFile = null;
      Exception primaryException = null;
      try {
        tmpFile = Files.createTempFile(tmpTableName + "-", ".tmp").toFile();
        writeBatchToFile(tmpFile, records);

        final ClickHouseConnection conn = connection.unwrap(ClickHouseConnection.class);
        final ClickHouseStatement sth = conn.createStatement();
        sth.write() // Write API entrypoint
            .table(String.format("%s.%s", schemaName, tmpTableName)) // where to write data
            .format(ClickHouseFormat.CSV) // set a format
            .data(tmpFile.getAbsolutePath()) // specify input
            .send();

      } catch (final Exception e) {
        primaryException = e;
        throw new RuntimeException(e);
      } finally {
        try {
          if (tmpFile != null) {
            Files.delete(tmpFile.toPath());
          }
        } catch (final IOException e) {
          if (primaryException != null) {
            e.addSuppressed(primaryException);
          }
          throw new RuntimeException(e);
        }
      }
    });
  }

}
