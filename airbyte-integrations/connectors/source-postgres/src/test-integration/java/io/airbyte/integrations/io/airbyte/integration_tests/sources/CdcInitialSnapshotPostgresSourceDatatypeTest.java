/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.standardtest.source.TestDataHolder;
import io.airbyte.cdk.integrations.standardtest.source.TestDestinationEnv;
import io.airbyte.cdk.testutils.PostgresTestDatabase;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.features.FeatureFlagsWrapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.JsonSchemaType;
import java.sql.SQLException;
import java.util.List;

public class CdcInitialSnapshotPostgresSourceDatatypeTest extends AbstractPostgresSourceDatatypeTest {

  private static final String SCHEMA_NAME = "test";
  private static final int INITIAL_WAITING_SECONDS = 30;

  private String slotName;
  private String publication;

  @Override
  protected FeatureFlags featureFlags() {
    return FeatureFlagsWrapper.overridingUseStreamCapableState(super.featureFlags(), true);
  }

  @Override
  protected Database setupDatabase() throws Exception {
    testdb = PostgresTestDatabase.make("postgres:16-bullseye", "withConf");
    slotName = testdb.withSuffix("debezium_slot");
    publication = testdb.withSuffix("publication");

    /**
     * The publication is not being set as part of the config and because of it
     * {@link io.airbyte.integrations.source.postgres.PostgresSource#isCdc(JsonNode)} returns false, as
     * a result no test in this class runs through the cdc path.
     */
    final JsonNode replicationMethod = Jsons.jsonNode(ImmutableMap.builder()
        .put("method", "CDC")
        .put("replication_slot", slotName)
        .put("publication", publication)
        .put("initial_waiting_seconds", INITIAL_WAITING_SECONDS)
        .build());
    config = Jsons.jsonNode(testdb.makeConfigBuilder()
        .put(JdbcUtils.SCHEMAS_KEY, List.of(SCHEMA_NAME))
        .put("replication_method", replicationMethod)
        .put("is_test", true)
        .put(JdbcUtils.SSL_KEY, false)
        .build());

    testdb.database.query(ctx -> {
      ctx.execute(
          "SELECT pg_create_logical_replication_slot('" + slotName + "', 'pgoutput');");
      ctx.execute("CREATE PUBLICATION " + publication + " FOR ALL TABLES;");
      ctx.execute("CREATE EXTENSION hstore;");
      return null;
    });

    testdb.database.query(ctx -> ctx.fetch("CREATE SCHEMA TEST;"));
    testdb.database.query(ctx -> ctx.fetch("CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');"));
    testdb.database.query(ctx -> ctx.fetch("CREATE TYPE inventory_item AS (\n"
        + "    name            text,\n"
        + "    supplier_id     integer,\n"
        + "    price           numeric\n"
        + ");"));

    testdb.database.query(ctx -> ctx.fetch("SET TIMEZONE TO 'MST'"));
    return testdb.database;
  }

  @Override
  protected void tearDown(TestDestinationEnv testEnv) throws SQLException {
    testdb.database.query(ctx -> {
      ctx.execute("SELECT pg_drop_replication_slot('" + slotName + "');");
      ctx.execute("DROP PUBLICATION " + publication + " CASCADE;");
      return null;
    });
    super.tearDown(testEnv);
  }

  public boolean testCatalog() {
    return true;
  }

  @Override
  protected void addHstoreTest() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("hstore")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("""
                             '"paperback" => "243","publisher" => "postgresqltutorial.com",
                             "language"  => "English","ISBN-13" => "978-1449370000",
                             "weight"    => "11.2 ounces"'
                             """, null)
            .addExpectedValues(
                //
                "\"weight\"=>\"11.2 ounces\", \"ISBN-13\"=>\"978-1449370000\", \"language\"=>\"English\", \"paperback\"=>\"243\", \"publisher\"=>\"postgresqltutorial.com\"",
                null)
            .build());
  }

}
