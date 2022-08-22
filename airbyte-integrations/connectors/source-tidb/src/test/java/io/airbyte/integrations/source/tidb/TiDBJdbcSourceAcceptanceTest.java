/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.tidb;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import com.mysql.cj.MysqlType;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import org.junit.jupiter.api.*;
import org.testcontainers.containers.GenericContainer;
import org.testcontainers.utility.DockerImageName;

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
        .put(JdbcUtils.HOST_KEY, "127.0.0.1")
        .put(JdbcUtils.PORT_KEY, container.getFirstMappedPort())
        .put(JdbcUtils.USERNAME_KEY, USER)
        .put(JdbcUtils.DATABASE_KEY, DATABASE)
        // .put(JdbcUtils.SSL_KEY, true)
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

  @AfterAll
  static void cleanUp() {
    container.close();
  }

}
