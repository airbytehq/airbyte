/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.tidb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.mysql.cj.MysqlType;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import org.junit.jupiter.api.*;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.utility.DockerImageName;

import java.sql.SQLException;

class TiDBJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  protected static GenericContainer container;
  protected static String USER = "root";
  protected static String DATABASE = "test";

  @BeforeEach
  public void setup() throws Exception {
    container = new GenericContainer(DockerImageName.parse("pingcap/tidb:nightly"))
        .withExposedPorts(4000);
    container.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", "127.0.0.1")
        .put("port", container.getFirstMappedPort())
        .put("username", USER)
        .put("database", DATABASE)
        // .put("ssl", true)
        .build());

    super.setup();
  }

  @AfterEach
  void tearDownTiDB() throws Exception {
    container.close();
    container.stop();
    super.tearDown();
  }

  @Override
  public AbstractJdbcSource<MysqlType> getSource() {
    return new TiDBSource();
  }

  @Override
  public boolean supportsSchemas() {
    return false;
  }

  @Override
  public JsonNode getConfig() {
    return Jsons.clone(config);
  }

  @Override
  public String getDriverClass() {
    return TiDBSource.DRIVER_CLASS;
  }

  @Override
  public AbstractJdbcSource<MysqlType> getJdbcSource() {
    return new TiDBSource();
  }

  @Override
  protected void createTableWithoutCursorFields() throws SQLException {
    database.execute(connection -> {
      connection.createStatement().execute(String.format("CREATE TABLE %s (jdoc JSON);", getFullyQualifiedTableName(TABLE_NAME_WITHOUT_CURSOR_FIELD)));
      connection.createStatement().execute(String.format("INSERT INTO %s VALUES('{\"key1\": \"value1\", \"key2\": \"value2\"}');", getFullyQualifiedTableName(TABLE_NAME_WITHOUT_CURSOR_FIELD)));
    });
  }

  @AfterAll
  static void cleanUp() {
    container.close();
  }

}
