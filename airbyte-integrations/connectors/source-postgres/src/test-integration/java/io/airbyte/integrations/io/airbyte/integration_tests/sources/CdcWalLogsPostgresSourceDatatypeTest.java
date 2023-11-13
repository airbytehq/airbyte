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
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.sql.SQLException;
import java.util.Collections;
import java.util.List;
import java.util.Set;

public class CdcWalLogsPostgresSourceDatatypeTest extends AbstractPostgresSourceDatatypeTest {

  private static final String SCHEMA_NAME = "test";
  private static final int INITIAL_WAITING_SECONDS = 30;
  private JsonNode stateAfterFirstSync;
  private String slotName;
  private String publication;

  @Override
  protected List<AirbyteMessage> runRead(final ConfiguredAirbyteCatalog configuredCatalog) throws Exception {
    if (stateAfterFirstSync == null) {
      throw new RuntimeException("stateAfterFirstSync is null");
    }
    return super.runRead(configuredCatalog, stateAfterFirstSync);
  }

  @Override
  protected void postSetup() throws Exception {
    final Database database = setupDatabase();
    initTests();
    for (final TestDataHolder test : testDataHolders) {
      database.query(ctx -> {
        ctx.fetch(test.getCreateSqlQuery());
        return null;
      });
    }

    final ConfiguredAirbyteStream dummyTableWithData = createDummyTableWithData(database);
    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog();
    catalog.getStreams().add(dummyTableWithData);

    final List<AirbyteMessage> allMessages = super.runRead(catalog);
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(allMessages);
    if (stateAfterFirstBatch == null || stateAfterFirstBatch.isEmpty()) {
      throw new RuntimeException("stateAfterFirstBatch should not be null or empty");
    }
    stateAfterFirstSync = Jsons.jsonNode(Collections.singletonList(stateAfterFirstBatch.get(stateAfterFirstBatch.size() - 1)));
    if (stateAfterFirstSync == null) {
      throw new RuntimeException("stateAfterFirstSync should not be null");
    }
    for (final TestDataHolder test : testDataHolders) {
      database.query(ctx -> {
        test.getInsertSqlQueries().forEach(ctx::fetch);
        return null;
      });
    }
  }

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
  protected void addMoneyTest() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("money")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues(
                "null",
                "'999.99'", "'1,001.01'", "'-1,000'",
                "'$999.99'", "'$1001.01'", "'-$1,000'"
            // max values for Money type: "-92233720368547758.08", "92233720368547758.07"
            // Debezium has wrong parsing for values more than 999999999999999 and less than -999999999999999
            // https://github.com/airbytehq/airbyte/issues/7338
            /* "'-92233720368547758.08'", "'92233720368547758.07'" */)
            .addExpectedValues(
                null,
                "999.99", "1001.01", "-1000.00",
                "999.99", "1001.01", "-1000.00"
            /* "-92233720368547758.08", "92233720368547758.07" */)
            .build());
  }

  @Override
  protected void addTimeWithTimeZoneTest() {
    // time with time zone
    for (final String fullSourceType : Set.of("timetz", "time with time zone")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType("timetz")
              .fullSourceDataType(fullSourceType)
              .airbyteType(JsonSchemaType.STRING_TIME_WITH_TIMEZONE)
              .addInsertValues("null", "'13:00:01'", "'13:00:00+8'", "'13:00:03-8'", "'13:00:04Z'", "'13:00:05.012345Z+8'", "'13:00:06.00000Z-8'")
              // A time value without time zone will use the time zone set on the database, which is Z-7,
              // so 13:00:01 is returned as 13:00:01-07.
              .addExpectedValues(null, "20:00:01Z", "05:00:00.000000Z", "21:00:03Z", "13:00:04Z", "21:00:05.012345Z",
                  "05:00:06Z")
              .build());
    }
  }

  @Override
  protected void addNumericValuesTest() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("numeric")
            .fullSourceDataType("NUMERIC(28,2)")
            .airbyteType(JsonSchemaType.NUMBER)
            .addInsertValues(
                "'123'", "null", "'14525.22'")
            // Postgres source does not support these special values yet
            // https://github.com/airbytehq/airbyte/issues/8902
            // "'infinity'", "'-infinity'", "'nan'"
            .addExpectedValues("123", null, "14525.22")
            .build());

    // Blocked by https://github.com/airbytehq/airbyte/issues/8902
    for (final String type : Set.of("numeric", "decimal")) {
      addDataTypeTestData(
          TestDataHolder.builder()
              .sourceType(type)
              .fullSourceDataType("NUMERIC(20,7)")
              .airbyteType(JsonSchemaType.NUMBER)
              .addInsertValues(
                  "'123'", "null", "'1234567890.1234567'")
              // Postgres source does not support these special values yet
              // https://github.com/airbytehq/airbyte/issues/8902
              // "'infinity'", "'-infinity'", "'nan'"
              .addExpectedValues("123", null, "1.2345678901234567E9")
              .build());
    }
  }

}
