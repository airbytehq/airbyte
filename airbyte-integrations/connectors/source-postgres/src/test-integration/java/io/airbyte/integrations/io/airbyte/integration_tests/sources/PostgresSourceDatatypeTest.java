/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.testutils.PostgresTestDatabase;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;
import io.airbyte.commons.json.Jsons;
import java.sql.SQLException;

public class PostgresSourceDatatypeTest extends AbstractPostgresSourceDatatypeTest {

  @Override
  protected FeatureFlags featureFlags() {
    return FeatureFlagsWrapper.overridingUseStreamCapableState(super.featureFlags(), true);
  }

  @Override
  protected Database setupDatabase() throws SQLException {
    testdb = PostgresTestDatabase.make("postgres:16-bullseye", "withConf");
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "Standard")
        .build());
    config = Jsons.jsonNode(testdb.makeConfigBuilder()
        .put(JdbcUtils.SSL_KEY, false)
        .put("replication_method", replicationMethod)
        .build());
    testdb.database.query(ctx -> {
      ctx.execute(String.format("CREATE SCHEMA %S;", SCHEMA_NAME));
      ctx.execute("CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');");
      ctx.execute("CREATE TYPE inventory_item AS (name text, supplier_id integer, price numeric);");
      // In one of the test case, we have some money values with currency symbol. Postgres can only
      // understand those money values if the symbol corresponds to the monetary locale setting. For
      // example,
      // if the locale is 'en_GB', '£100' is valid, but '$100' is not. So setting the monetary locate is
      // necessary here to make sure the unit test can pass, no matter what the locale the runner VM has.
      ctx.execute("SET lc_monetary TO 'en_US.utf8';");
      // Set up a fixed timezone here so that timetz and timestamptz always have the same time zone
      // wherever the tests are running on.
      ctx.execute("SET TIMEZONE TO 'MST'");
      ctx.execute("CREATE EXTENSION hstore;");
      return null;
    });

    return testdb.database;
  }

  @Override
  public boolean testCatalog() {
    return true;
  }

}
