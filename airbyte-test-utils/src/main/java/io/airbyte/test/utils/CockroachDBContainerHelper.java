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
import io.airbyte.db.Databases;
import io.airbyte.db.jdbc.JdbcDatabase;
import java.io.IOException;
import java.util.UUID;
import org.jooq.SQLDialect;
import org.testcontainers.containers.CockroachContainer;
import org.testcontainers.utility.MountableFile;

public class CockroachDBContainerHelper {

  public static void runSqlScript(MountableFile file, CockroachContainer db) {
    try {
      String scriptPath = "/etc/" + UUID.randomUUID() + ".sql";
      db.copyFileToContainer(file, scriptPath);
      db.execInContainer(
          "cockroach", "sql", "-d", db.getDatabaseName(), "-u", db.getUsername(), "-f", scriptPath,
          "--insecure");

    } catch (InterruptedException | IOException e) {
      throw new RuntimeException(e);
    }
  }

  public static JsonNode createDatabaseWithRandomNameAndGetPostgresConfig(
                                                                          CockroachContainer psqlDb) {
    final String dbName = Strings.addRandomSuffix("db", "_", 10).toLowerCase();
    return createDatabaseAndGetPostgresConfig(psqlDb, dbName);
  }

  public static JsonNode createDatabaseAndGetPostgresConfig(CockroachContainer psqlDb,
                                                            String dbName) {
    final String initScriptName = "init_" + dbName.concat(".sql");
    final String tmpFilePath = IOs
        .writeFileToRandomTmpDir(initScriptName, "CREATE DATABASE " + dbName + ";");
    CockroachDBContainerHelper.runSqlScript(MountableFile.forHostPath(tmpFilePath), psqlDb);

    return getDestinationConfig(psqlDb, dbName);
  }

  public static JsonNode getDestinationConfig(CockroachContainer psqlDb, String dbName) {
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

  public static Database getDatabaseFromConfig(JsonNode config) {
    return Databases.createDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:postgresql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        "org.postgresql.Driver",
        SQLDialect.POSTGRES);
  }

  public static JdbcDatabase getJdbcDatabaseFromConfig(JsonNode config) {
    return Databases.createJdbcDatabase(
        config.get("username").asText(),
        config.get("password").asText(),
        String.format("jdbc:postgresql://%s:%s/%s",
            config.get("host").asText(),
            config.get("port").asText(),
            config.get("database").asText()),
        "org.postgresql.Driver");
  }

}
