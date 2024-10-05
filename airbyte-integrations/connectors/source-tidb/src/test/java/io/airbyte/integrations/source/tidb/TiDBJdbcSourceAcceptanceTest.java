/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.tidb;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.commons.json.Jsons;
import org.testcontainers.tidb.TiDBContainer;

class TiDBJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest<TiDBSource, TiDBTestDatabase> {

  private final TiDBContainer container = TiDBTestDatabase.container();

  @Override
  public boolean supportsSchemas() {
    return false;
  }

  @Override
  public JsonNode config() {
    return Jsons.clone(testdb.testConfigBuilder().build());
  }

  @Override
  protected TiDBSource source() {
    return new TiDBSource();
  }

  @Override
  protected TiDBTestDatabase createTestDatabase() {
    return new TiDBTestDatabase(container).initialized();
  }

}
