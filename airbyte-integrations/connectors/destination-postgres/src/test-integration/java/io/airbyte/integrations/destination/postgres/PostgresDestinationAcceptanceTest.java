/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.postgres;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.integrations.destination.postgres.PostgresTestDatabase.BaseImage;
import java.util.HashSet;

public class PostgresDestinationAcceptanceTest extends AbstractPostgresDestinationAcceptanceTest {

  private PostgresTestDatabase testDb;

  @Override
  protected JsonNode getConfig() {
    return testDb.configBuilder()
        .with("schema", "public")
        .withDatabase()
        .withResolvedHostAndPort()
        .withCredentials()
        .withoutSsl()
        .build();
    /*return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, HostPortResolver.resolveHost(db))
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.SCHEMA_KEY, "public")
        .put(JdbcUtils.PORT_KEY, HostPortResolver.resolvePort(db))
        .put(JdbcUtils.DATABASE_KEY, db.getDatabaseName())
        .put(JdbcUtils.SSL_KEY, false)
        .build());*/
  }

  @Override
  protected PostgresTestDatabase getTestDb() {
    return testDb;
  }

  @Override
  protected void setup(final TestDestinationEnv testEnv, final HashSet<String> TEST_SCHEMAS) {
    testDb = PostgresTestDatabase.in(BaseImage.POSTGRES_13);
  }

  @Override
  protected void tearDown(final TestDestinationEnv testEnv) {
    testDb.close();
  }

}
