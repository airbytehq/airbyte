/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.integrations.source.redshift.RedshiftSource;
import java.nio.file.Path;
import java.sql.JDBCType;
import java.sql.SQLException;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;

// Run as part of integration tests, instead of unit tests, because there is no test container for
// Redshift.
class RedshiftJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  private JsonNode config;

  private static JsonNode getStaticConfig() {
    return Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  @BeforeAll
  static void init() {
    CREATE_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "CREATE TABLE %s (%s GEOMETRY)";
    INSERT_TABLE_WITHOUT_CURSOR_TYPE_QUERY = "INSERT INTO %s VALUES(ST_Point(129.77099609375, 62.093299865722656))";
  }

  @BeforeEach
  public void setup() throws Exception {
    config = getStaticConfig();
    super.setup();
  }

  @Override
  public boolean supportsSchemas() {
    return true;
  }

  @Override
  public AbstractJdbcSource<JDBCType> getJdbcSource() {
    return new RedshiftSource();
  }

  @Override
  public JsonNode getConfig() {
    return config;
  }

  @Override
  public String getDriverClass() {
    return RedshiftSource.DRIVER_CLASS;
  }

  @AfterEach
  public void tearDownRedshift() throws SQLException {
    super.tearDown();
  }

}
