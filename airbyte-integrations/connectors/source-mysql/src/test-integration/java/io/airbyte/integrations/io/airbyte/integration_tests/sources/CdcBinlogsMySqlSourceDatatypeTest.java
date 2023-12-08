/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.Iterables;
import io.airbyte.cdk.db.Database;
import io.airbyte.cdk.integrations.standardtest.source.TestDataHolder;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase;
import io.airbyte.integrations.source.mysql.MySQLTestDatabase.BaseImage;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.util.List;

public class CdcBinlogsMySqlSourceDatatypeTest extends AbstractMySqlSourceDatatypeTest {

  private JsonNode stateAfterFirstSync;

  @Override
  protected JsonNode getConfig() {
    return testdb.integrationTestConfigBuilder()
        .withoutSsl()
        .withCdcReplication()
        .build();
  }

  @Override
  protected Database setupDatabase() {
    testdb = MySQLTestDatabase.in(BaseImage.MYSQL_8).withoutStrictMode().withCdcPermissions();
    return testdb.getDatabase();
  }

  @Override
  protected List<AirbyteMessage> runRead(final ConfiguredAirbyteCatalog configuredCatalog) throws Exception {
    if (stateAfterFirstSync == null) {
      throw new RuntimeException("stateAfterFirstSync is null");
    }
    return super.runRead(configuredCatalog, stateAfterFirstSync);
  }

  @Override
  protected void postSetup() throws Exception {
    final var database = testdb.getDatabase();
    for (final TestDataHolder test : testDataHolders) {
      database.query(ctx -> {
        ctx.execute("TRUNCATE TABLE " + test.getNameWithTestPrefix() + ";");
        return null;
      });
    }

    final ConfiguredAirbyteStream dummyTableWithData = createDummyTableWithData(database);
    final ConfiguredAirbyteCatalog catalog = getConfiguredCatalog();
    catalog.getStreams().add(dummyTableWithData);

    final List<AirbyteMessage> allMessages = super.runRead(catalog);
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(allMessages);
    stateAfterFirstSync = Jsons.jsonNode(List.of(Iterables.getLast(stateAfterFirstBatch)));
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
  public boolean testCatalog() {
    return true;
  }

  @Override
  protected void addTimestampDataTypeTest() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("timestamp")
            .airbyteType(JsonSchemaType.STRING_TIMESTAMP_WITH_TIMEZONE)
            .addInsertValues("null", "'2021-01-00'", "'2021-00-00'", "'0000-00-00'", "'2022-08-09T10:17:16.161342Z'")
            .addExpectedValues(null, "1970-01-01T00:00:00.000000Z", "1970-01-01T00:00:00.000000Z", "1970-01-01T00:00:00.000000Z",
                "2022-08-09T10:17:16.000000Z")
            .build());
  }

  @Override
  protected void addJsonDataTypeTest() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("json")
            .airbyteType(JsonSchemaType.STRING)
            .addInsertValues("null", "'{\"a\":10,\"b\":15}'", "'{\"fóo\":\"bär\"}'", "'{\"春江潮水连海平\":\"海上明月共潮生\"}'")
            .addExpectedValues(null, "{\"a\":10,\"b\":15}", "{\"fóo\":\"bär\"}", "{\"春江潮水连海平\":\"海上明月共潮生\"}")
            .build());
  }

  @Override
  protected void addDecimalValuesTest() {
    addDataTypeTestData(
        TestDataHolder.builder()
            .sourceType("decimal")
            .airbyteType(JsonSchemaType.NUMBER)
            .fullSourceDataType("decimal(19,2)")
            .addInsertValues("1700000.01", "'123'")
            .addExpectedValues("1700000.01", "123.00")
            .build());
  }

}
