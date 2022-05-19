/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.test.utils;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.db.Database;
import io.airbyte.db.factory.DataSourceFactory;
import io.airbyte.db.factory.DatabaseDriver;
import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcUtils;
import java.io.IOException;
import java.util.UUID;
import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.testcontainers.containers.CockroachContainer;
import org.testcontainers.utility.MountableFile;

public class CockroachDBContainerHelper {

  public static void runSqlScript(final MountableFile file, final CockroachContainer db) {
    try {
      final String scriptPath = "/etc/" + UUID.randomUUID() + ".sql";
      db.copyFileToContainer(file, scriptPath);
      db.execInContainer(
          "cockroach", "sql", "-d", db.getDatabaseName(), "-u", db.getUsername(), "-f", scriptPath,
          "--insecure");

    } catch (final InterruptedException | IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static JsonNode createDatabaseWithRandomNameAndGetPostgresConfig(
                                                                          final CockroachContainer psqlDb) {
    final String dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();
    return createDatabaseAndGetPostgresConfig(psqlDb, dbName);
  }

  public static JsonNode createDatabaseAndGetPostgresConfig(final CockroachContainer psqlDb,
                                                            final String dbName) {
    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs
        .writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    CockroachDBContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), psqlDb);

    return getDestinationConfig(psqlDb, dbName);
  }

  public static JsonNode getDestinationConfig(final CockroachContainer psqlDb, final String dbName) {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put("host", psqlDb.getHost())
        .put("port", psqlDb.getFirstMappedPort())
        .put("database", dbName)
        .put("username", psqlDb.getUsername())
        .put("password", psqlDb.getPassword())
        .put("schema", "public")
        .put("ssl", false)
        .build());
  }

  public static DataSource getDataSourceFromConfig(final JsonNode config) {
    return DataSourceFactory.create(
        config.get("username").asText(),
        config.get("password").asText(),
        DatabaseDriver.POSTGRESQL.getDriverClassName(),
        String.format(DatabaseDriver.POSTGRESQL.getUrlFormatString(),
            config.get("host").asText(),
            config.get("port").asInt(),
            config.get("database").asText()));
  }

  public static Database getDatabaseFromConfig(final DSLContext dslContext) {// final JsonNode config) {
    return new Database(dslContext);
  }

  public static JdbcDatabase getJdbcDatabaseFromConfig(final DataSource dataSource) { // final JsonNode config) {
    return new DefaultJdbcDatabase(dataSource, JdbcUtils.getDefaultSourceOperations());
  }

}
