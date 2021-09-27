/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.clickhouse.ClickHouseSource;
import io.airbyte.integrations.source.jdbc.AbstractJdbcSource;
import io.airbyte.integrations.source.jdbc.test.JdbcStressTest;
import java.util.Optional;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Disabled;
import org.testcontainers.containers.ClickHouseContainer;

@Disabled
public class ClickHouseJdbcStressTest extends JdbcStressTest {

  private static final String SCHEMA_NAME = "default";
  private ClickHouseContainer db;
  private JsonNode config;

  @Override
  public Optional<String> getDefaultSchemaName() {
    return Optional.of(SCHEMA_NAME);
  }

  @Override
  @BeforeEach
  public void setup() throws Exception {
    db = new ClickHouseContainer("yandex/clickhouse-server:21.3.10.1-alpine");
    db.start();

    config = Jsons.jsonNode(ImmutableMap.builder()
        .put("host", db.getHost())
        .put("port", db.getFirstMappedPort())
        .put("database", SCHEMA_NAME)
        .put("username", db.getUsername())
        .put("password", db.getPassword())
        .build());

    super.setup();
  }

  @Override
  protected String createTableQuery(String tableName, String columnClause) {
    // ClickHouse requires Engine to be mentioned as part of create table query.
    // Refer : https://clickhouse.tech/docs/en/engines/table-engines/ for more information
    return String.format("CREATE TABLE %s(%s) %s",
        tableName, columnClause, "ENGINE = TinyLog");
  }

  @AfterEach
  public void tearDown() {
    db.close();
    db.stop();
  }

  @Override
  public JsonNode getConfig() {
    return Jsons.clone(config);
  }

  @Override
  public String getDriverClass() {
    return ClickHouseSource.DRIVER_CLASS;
  }

  @Override
  public AbstractJdbcSource getSource() {
    return new ClickHouseSource();
  }

}
