/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore;

import static io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.executeTypeAndDedupe;
import static org.junit.jupiter.api.Assertions.assertAll;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableMap;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcSourceOperations;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.destination.typing_deduping.*;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState;
import io.airbyte.integrations.destination.singlestore.jdbc.SingleStoreDestinationHandler;
import io.airbyte.integrations.destination.singlestore.jdbc.SingleStoreNamingTransformer;
import io.airbyte.integrations.destination.singlestore.jdbc.SingleStoreSqlGenerator;
import io.airbyte.protocol.models.v0.*;
import java.io.IOException;
import java.sql.SQLException;
import java.text.MessageFormat;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.function.BiFunction;
import java.util.stream.Collectors;
import org.apache.commons.lang3.RandomStringUtils;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;

public class SingleStoreSqlGeneratorIntegrationTest extends BaseSqlGeneratorIntegrationTest<MinimumDestinationState.Impl> {

  private static AirbyteSingleStoreTestContainer db;

  @BeforeAll
  static void setupTestContainer() throws IOException, InterruptedException {
    AirbyteSingleStoreTestContainer container = new AirbyteSingleStoreTestContainer();
    container.start();
    final String username = "user_" + RandomStringUtils.randomAlphabetic(5).toLowerCase();
    final String password = RandomStringUtils.randomAlphabetic(10).toLowerCase();
    final String[] sql =
        new String[] {String.format("CREATE USER %s IDENTIFIED BY '%s'", username, password), String.format("GRANT ALL ON *.* TO %s", username)};
    container.execInContainer("/bin/bash", "-c",
        String.format("set -o errexit -o pipefail; echo \"%s\" | singlestore -v -v -v --user=root --password=root", String.join("; ", sql)));
    db = container.withUsername(username).withPassword(password);
  }

  private JsonNode getConfig() {
    return Jsons.jsonNode(ImmutableMap.builder()
        .put(JdbcUtils.HOST_KEY, db.getHost())
        .put(JdbcUtils.PORT_KEY, db.getFirstMappedPort())
        .put(JdbcUtils.DATABASE_KEY, getNamespace())
        .put(JdbcUtils.USERNAME_KEY, db.getUsername())
        .put(JdbcUtils.PASSWORD_KEY, db.getPassword())
        .put(JdbcUtils.SSL_KEY, false).build());
  }

  private JdbcDatabase getJdbcDatabase() {
    var datasource = SingleStoreConnectorFactory.createDataSource(getConfig());
    return new DefaultJdbcDatabase(datasource);
  }

  @NotNull
  @Override
  protected DestinationHandler<MinimumDestinationState.Impl> getDestinationHandler() {
    return new SingleStoreDestinationHandler(getJdbcDatabase());
  }

  @Override
  protected SingleStoreSqlGenerator getSqlGenerator() {
    return new SingleStoreSqlGenerator(new SingleStoreNamingTransformer());
  }

  @Override
  protected boolean getSupportsSafeCast() {
    return true;
  }

  @Override
  protected void createNamespace(@NotNull String namespace) throws Exception {
    setNamespace(namespace);
    db.execInContainer("/bin/bash", "-c",
        String.format("set -o errexit -o pipefail; echo \"%s\" | singlestore -v -v -v --user=root --password=root",
            String.join("; ", String.format("CREATE DATABASE %s", namespace))));
  }

  @Override
  protected void createRawTable(@NotNull StreamId streamId) throws Exception {
    getDestinationHandler().execute(getSqlGenerator().createRawTable(streamId));
  }

  @Override
  protected void createV1RawTable(@NotNull StreamId streamId) throws Exception {
    // not supported
  }

  @Override
  protected void insertRawTableRecords(@NotNull StreamId streamId, @NotNull List<? extends JsonNode> records) throws Exception {
    var columnNames =
        List.of(
            JavaBaseConstants.COLUMN_NAME_AB_RAW_ID,
            JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT,
            JavaBaseConstants.COLUMN_NAME_DATA,
            JavaBaseConstants.COLUMN_NAME_AB_META);
    var tableIdentifier = streamId.rawTableId(SingleStoreSqlGenerator.QUOTE);
    insertRecords(columnNames, tableIdentifier, records);
  }

  private void insertRecords(
                             List<String> columnNames,
                             String tableIdentifier,
                             List<? extends JsonNode> records)
      throws Exception {
    BiFunction<String, JsonNode, String> mapper = (String name, JsonNode record) -> {
      JsonNode node = record.get(name);
      if (node == null) {
        return "NULL";
      } else if (JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT.equals(name) || JavaBaseConstants.COLUMN_NAME_AB_LOADED_AT.equals(name)
          || "_ab_cdc_deleted_at".equals(name)) {
        return String.format("'%s'", node.asText().replace("Z", ""));
      } else if (JavaBaseConstants.COLUMN_NAME_DATA.equals(name)) {
        return String.format("\"%s\"", node.toString().replace("\\", "\\\\").replace("\"", "\\\""));
      } else if (node.isTextual() || node.isNumber()) {
        return String.format("'%s'", node.asText());
      } else {
        return String.format("'%s'", node);
      }
    };
    var columnNamesSrt =
        columnNames.stream().map(c -> MessageFormat.format("{0}{1}{0}", SingleStoreSqlGenerator.QUOTE, c)).collect(Collectors.joining(", "));
    for (JsonNode r : records) {
      var valuesSrt = columnNames.stream().map(n -> mapper.apply(n, r)).collect(Collectors.joining(", "));
      var insertStmt = MessageFormat.format("INSERT INTO {0}({1}) VALUES ({2})",
          tableIdentifier, columnNamesSrt, valuesSrt);
      getDestinationHandler().execute(Sql.of(insertStmt));
    }
  }

  @Override
  protected void insertV1RawTableRecords(@NotNull StreamId streamId, @NotNull List<? extends JsonNode> list) throws Exception {
    // not supported
  }

  @Override
  protected void insertFinalTableRecords(boolean includeCdcDeletedAt,
                                         @NotNull StreamId streamId,
                                         @Nullable String suffix,
                                         @NotNull List<? extends JsonNode> records,
                                         long generationId)
      throws Exception {
    var columnNames = includeCdcDeletedAt ? FINAL_TABLE_COLUMN_NAMES_CDC : FINAL_TABLE_COLUMN_NAMES;
    var tableIdentifier = streamId.finalTableId(SingleStoreSqlGenerator.QUOTE, suffix == null ? "" : suffix);
    insertRecords(columnNames, tableIdentifier, records);
  }

  @NotNull
  @Override
  protected List<JsonNode> dumpRawTableRecords(@NotNull StreamId streamId) throws Exception {
    return dumpTable(streamId.rawTableId(SingleStoreSqlGenerator.QUOTE));
  }

  @NotNull
  @Override
  protected List<JsonNode> dumpFinalTableRecords(@NotNull StreamId streamId, @Nullable String suffix) throws Exception {
    return dumpTable(streamId.finalTableId(SingleStoreSqlGenerator.QUOTE, suffix == null ? "" : suffix));
  }

  private List<JsonNode> dumpTable(String tableIdentifier) throws SQLException {
    var sourceOperations =
        new JdbcSourceOperations() {};
    return getJdbcDatabase().bufferedResultSetQuery(
        connection -> connection.createStatement().executeQuery(MessageFormat.format("SELECT * FROM {0} ORDER BY {1} ASC",
            tableIdentifier, JavaBaseConstants.COLUMN_NAME_AB_EXTRACTED_AT)),
        sourceOperations::rowToJson);
  }

  @Test
  @Override
  public void testLongIdentifierHandling() {
    var randomSuffix = Strings.addRandomSuffix("", "_", 5);
    var rawNamespace = "some_namespacerandomsuffix";
    var finalNamespace = "b".repeat(54) + randomSuffix;
    var streamName = "c".repeat(54) + randomSuffix;
    var baseColumnName = "d".repeat(60) + randomSuffix;
    var columnName1 = baseColumnName + "1";
    var columnName2 = baseColumnName + "2";

    var catalogParser = new CatalogParser(getGenerator(), rawNamespace);
    var stream =
        catalogParser
            .parseCatalog(new ConfiguredAirbyteCatalog().withStreams(Collections.singletonList(new ConfiguredAirbyteStream()
                .withStream(new AirbyteStream().withName(streamName).withNamespace(finalNamespace)
                    .withJsonSchema(io.airbyte.protocol.models.Jsons.jsonNode(Map.of("type", "object", "properties",
                        Map.of(columnName1, Map.of("type", "string"), columnName2, Map.of("type", "string"))))))
                .withSyncMode(SyncMode.INCREMENTAL).withDestinationSyncMode(DestinationSyncMode.APPEND))))
            .getStreams().iterator().next();
    var streamId = stream.getId();
    ColumnId columnId1 = stream.getColumns().entrySet().stream().filter(e -> columnName1.equals(e.getKey().getOriginalName())).findFirst()
        .map(Map.Entry::getKey).orElse(null);
    ColumnId columnId2 = stream.getColumns().entrySet().stream().filter(e -> columnName2.equals(e.getKey().getOriginalName())).findFirst()
        .map(Map.Entry::getKey).orElse(null);
    try {
      createNamespace(rawNamespace);
      createNamespace(finalNamespace);
      createRawTable(streamId);
      insertRawTableRecords(streamId,
          List.of(io.airbyte.protocol.models.Jsons.jsonNode(Map.of("_airbyte_raw_id", "ad3e8c84-e02e-4df4-b146-3d5a007b21b4",
              "_airbyte_extracted_at", "2023-01-01T00:00:00", "_airbyte_data", Map.of(columnName1, "foo", columnName2, "bar")))));
      var createTable = getGenerator().createTable(stream, "", false);
      getDestinationHandler().execute(createTable);
      executeTypeAndDedupe(getGenerator(), getDestinationHandler(), stream, Optional.empty(), "");

      var rawRecords = dumpRawTableRecords(streamId);
      var finalRecords = dumpFinalTableRecords(streamId, "");
      assertAll(() -> Assertions.assertEquals(1, rawRecords.size()), () -> Assertions.assertEquals(1, finalRecords.size()),
          // Assume that if we can find the values in the final table, that everything looks
          // right :shrug:
          () -> Assertions.assertEquals("foo", finalRecords.get(0).get(columnId1.getName()).asText()),
          () -> Assertions.assertEquals("bar", finalRecords.get(0).get(columnId2.getName()).asText()));
    } catch (Exception e) {
      throw new RuntimeException(e);
    } finally {
      // do this manually b/c we're using a weird namespace that won't get handled by the
      // @AfterEach method
      try {
        teardownNamespace(rawNamespace);
        teardownNamespace(finalNamespace);
      } catch (Exception e) {
        //
      }
    }
  }

  @Disabled("No V1 Table migration for SingleStore")
  public void testV1V2migration() {}

  @Disabled("No state table in SingleStore")
  public void testStateHandling() throws Exception {
    super.testStateHandling();
  }

  @Override
  protected void teardownNamespace(@NotNull String s) throws Exception {
    db.execInContainer("/bin/bash", "-c",
        String.format("set -o errexit -o pipefail; echo \"%s\" | singlestore -v -v -v --user=root --password=root",
            String.join("; ", String.format("DROP DATABASE IF EXISTS %s", s))));
  }

  @Disabled
  @Override
  public void testCreateTableIncremental() throws Exception {

  }

}
