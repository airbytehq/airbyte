/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.tidb;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.integrations.source.jdbc.test.JdbcSourceAcceptanceTest;
import io.airbyte.commons.json.Jsons;
import org.junit.jupiter.api.Disabled;
import org.testcontainers.tidb.TiDBContainer;
import org.testcontainers.utility.DockerImageName;

@Disabled
class TiDBJdbcSourceAcceptanceTest extends JdbcSourceAcceptanceTest<TiDBSource, TiDBTestDatabase> {

  @Override
  public boolean supportsSchemas() {
    return false;
  }

  @Override
  public JsonNode config() {
    return Jsons.clone(testdb.configBuilder().build());
  }

  @Override
  protected TiDBSource source() {
    return new TiDBSource();
  }

  @Override
  protected TiDBTestDatabase createTestDatabase() {
    final TiDBContainer container = new TiDBContainer(DockerImageName.parse("pingcap/tidb:nightly"))
        .withExposedPorts(4000);
    container.start();
    return new TiDBTestDatabase(container).initialized();
  }

}
