/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.integrations.source.redshift.RedshiftSource;
import java.nio.file.Path;
import java.sql.JDBCType;
import java.sql.SQLException;
import java.util.List;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;

// Run as part of integration tests, instead of unit tests, because there is no test container for
// Redshift.
class RedshiftJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest {

  private ObjectNode config;

  private static ObjectNode getStaticConfig() {
    return (ObjectNode) Jsons.deserialize(IOs.readFile(Path.of("secrets/config.json")));
  }

  @BeforeEach
  public void setup() throws Exception {
    config = getStaticConfig();
    // limit the connection to one schema only
    config = config.set("schemas", Jsons.jsonNode(List.of(SCHEMA_NAME, SCHEMA_NAME2)));

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
