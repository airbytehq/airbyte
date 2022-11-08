/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.scaffold_java_jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import java.sql.JDBCType;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

class ScaffoldJavaJdbcJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(ScaffoldJavaJdbcJdbcSourceAcceptanceTest.class);

  // TODO declare a test container for DB. EX: org.testcontainers.containers.OracleContainer

  @BeforeAll
  static void init() {
    // Oracle returns uppercase values
    // TODO init test container. Ex: "new OracleContainer("epiclabs/docker-oracle-xe-11g")"
    // TODO start container. Ex: "container.start();"
  }

  @BeforeEach
  public void setup() throws Exception {
    // TODO init config. Ex: "config = Jsons.jsonNode(ImmutableMap.builder().put("host",
    // host).put("port", port)....build());
    super.setup();
  }

  @AfterEach
  public void tearDown() {
    // TODO clean used resources
  }

  @Override
  public AbstractJdbcSource<JDBCType> getSource() {
    return new ScaffoldJavaJdbcSource();
  }

  @Override
  public boolean supportsSchemas() {
    // TODO check if your db supports it and update method accordingly
    return false;
  }

  @Override
  public JsonNode getConfig() {
    return config;
  }

  @Override
  public String getDriverClass() {
    return ScaffoldJavaJdbcSource.DRIVER_CLASS;
  }

  @Override
  public AbstractJdbcSource<JDBCType> getJdbcSource() {
    // TODO
    return null;
  }

  @AfterAll
  static void cleanUp() {
    // TODO close the container. Ex: "container.close();"
  }

}
