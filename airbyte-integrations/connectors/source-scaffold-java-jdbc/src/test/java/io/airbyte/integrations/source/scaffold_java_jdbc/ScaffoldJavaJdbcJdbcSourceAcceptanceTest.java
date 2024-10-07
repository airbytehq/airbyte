/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.scaffold_java_jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import org.junit.jupiter.api.Disabled;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Disabled
class ScaffoldJavaJdbcJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest<ScaffoldJavaJdbcSource, ScaffoldJavaJdbcTestDatabase> {

  private static final Logger LOGGER = LoggerFactory.getLogger(ScaffoldJavaJdbcJdbcSourceAcceptanceTest.class);

  @Override
  protected JsonNode config() {
    // TODO: (optional) call more builder methods.
    return testdb.testConfigBuilder().build();
  }

  @Override
  protected ScaffoldJavaJdbcSource source() {
    // TODO: (optional) call `setFeatureFlags` before returning the source to mock setting env vars.
    return new ScaffoldJavaJdbcSource();
  }

  @Override
  protected ScaffoldJavaJdbcTestDatabase createTestDatabase() {
    // TODO: return a suitable TestDatabase instance.
    return new ScaffoldJavaJdbcTestDatabase(null).initialized();
  }

  @Override
  public boolean supportsSchemas() {
    // TODO check if your db supports it and update method accordingly
    return false;
  }

}
