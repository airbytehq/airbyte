/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.io.airbyte.integration_tests.sources;


import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.db.Database;
import io.airbyte.integrations.standardtest.source.TestDataHolder;
import io.airbyte.protocol.models.JsonSchemaType;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import java.nio.file.Path;
import java.util.List;

public class CdcBinlogsMySqlSourceDatatypeTest extends AbstractMySqlSourceDatatypeTest {

  private JsonNode stateAfterFirstSync;

  @Override
  protected Path getConfigFilePath() {
    return Path.of("secrets/cdc-binlogs-mysql-source-datatype-test-config.json");
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
    if (allMessages.size() != 2) {
      throw new RuntimeException("First sync should only generate 2 records");
    }
    final List<AirbyteStateMessage> stateAfterFirstBatch = extractStateMessages(allMessages);
    if (stateAfterFirstBatch == null || stateAfterFirstBatch.isEmpty()) {
      throw new RuntimeException("stateAfterFirstBatch should not be null or empty");
    }
    stateAfterFirstSync = Jsons.jsonNode(stateAfterFirstBatch);
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

}
