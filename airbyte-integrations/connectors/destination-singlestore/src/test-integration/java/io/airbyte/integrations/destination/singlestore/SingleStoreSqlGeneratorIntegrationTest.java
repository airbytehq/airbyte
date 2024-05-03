/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore;

import static io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.executeSoftReset;
import static io.airbyte.integrations.base.destination.typing_deduping.TyperDeduperUtil.executeTypeAndDedupe;
import static io.airbyte.integrations.destination.singlestore.typing_deduping.SingleStoreSqlGenerator.JSON_TYPE;
import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcDatabase;
import io.airbyte.cdk.db.jdbc.JdbcUtils;
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcSqlGenerator;
import io.airbyte.cdk.integrations.standardtest.destination.typing_deduping.JdbcSqlGeneratorIntegrationTest;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.destination.typing_deduping.*;
import io.airbyte.integrations.base.destination.typing_deduping.migrators.MinimumDestinationState;
import io.airbyte.integrations.destination.singlestore.typing_deduping.DslUtils;
import io.airbyte.integrations.destination.singlestore.typing_deduping.SingleStoreDestinationHandler;
import io.airbyte.integrations.destination.singlestore.typing_deduping.SingleStoreSqlGenerator;
import io.airbyte.protocol.models.Jsons;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.time.Instant;
import java.util.*;
import javax.sql.DataSource;
import org.jetbrains.annotations.NotNull;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.SQLDialect;
import org.jooq.conf.ParamType;
import org.jooq.impl.DSL;
import org.junit.jupiter.api.*;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

@Execution(ExecutionMode.SAME_THREAD)
public class SingleStoreSqlGeneratorIntegrationTest extends JdbcSqlGeneratorIntegrationTest<MinimumDestinationState> {

  private static SingleStoreTestDatabase testContainer;
  private static String databaseName;
  private static JdbcDatabase database;
  private static JsonNode config;

  @Override
  protected boolean getSupportsSafeCast() {
    return true;
  }

  @BeforeAll
  public static void setupSingleStore() {
    testContainer = SingleStoreTestDatabase.in(SingleStoreTestDatabase.BaseImage.SINGLESTORE_DEV);
    config = testContainer.configBuilder().withDatabase().withHostAndPort().withCredentials().withoutSsl().build();

    databaseName = config.get(JdbcUtils.DATABASE_KEY).asText();
    final SingleStoreDestination destination = new SingleStoreDestination();
    final DataSource dataSource = destination.getDataSource(config);
    database = new DefaultJdbcDatabase(dataSource);
  }

  @Test
  @Override
  public void softReset() throws Exception {
    createRawTable(getStreamId());
    createFinalTable(getCdcIncrementalAppendStream(), "");
    insertRawTableRecords(getStreamId(), List.of(Jsons.deserialize("""
                                                                   {
                                                                     "_airbyte_raw_id": "arst",
                                                                     "_airbyte_extracted_at": "2023-01-01T00:00:00",
                                                                     "_airbyte_loaded_at": "2023-01-01T00:00:00",
                                                                     "_airbyte_data": {
                                                                       "id1": 1,
                                                                       "id2": 100,
                                                                       "_ab_cdc_deleted_at": "2023-01-01T00:01:00"
                                                                     }
                                                                   }
                                                                   """)));
    insertFinalTableRecords(true, getStreamId(), "", List.of(Jsons.deserialize("""
                                                                               {
                                                                                 "_airbyte_raw_id": "arst",
                                                                                 "_airbyte_extracted_at": "2023-01-01T00:00:00",
                                                                                 "_airbyte_meta": {},
                                                                                 "id1": 1,
                                                                                 "id2": 100,
                                                                                 "_ab_cdc_deleted_at": "2023-01-01T00:01:00"
                                                                               }
                                                                               """)), 0);
    executeSoftReset(getSqlGenerator(), getDestinationHandler(), getIncrementalAppendStream());

    var actualRawRecords = dumpRawTableRecords(getStreamId());
    var actualFinalRecords = dumpFinalTableRecords(getStreamId(), "");
    Assertions.assertAll(() -> Assertions.assertEquals(1, actualRawRecords.size()), () -> Assertions.assertEquals(1, actualFinalRecords.size()),
        () -> Assertions.assertTrue(actualFinalRecords.stream().noneMatch(r -> r.has("_ab_cdc_deleted_at")),
            "_ab_cdc_deleted_at column was expected to be dropped. Actual final table had: $actualFinalRecords"));
  }

  @Override
  @Test
  public void cdcIdempotent() throws Exception {
    createRawTable(getStreamId());
    createFinalTable(getCdcIncrementalAppendStream(), "");
    insertRawTableRecords(getStreamId(), List.of(Jsons.deserialize("""
                                                                   {
                                                                     "_airbyte_raw_id": "4fa4efe2-3097-4464-bd22-11211cc3e15b",
                                                                     "_airbyte_extracted_at": "2023-01-01T00:00:00",
                                                                     "_airbyte_data": {
                                                                       "id1": 1,
                                                                       "id2": 100,
                                                                       "updated_at": "2023-01-01T00:00:00",
                                                                       "_ab_cdc_deleted_at": "2023-01-01T00:01:00"
                                                                     }
                                                                   }
                                                                   """)));

    // Execute T+D twice
    executeTypeAndDedupe(getSqlGenerator(), getDestinationHandler(), getCdcIncrementalAppendStream(), Optional.empty(), "");
    executeTypeAndDedupe(getSqlGenerator(), getDestinationHandler(), getCdcIncrementalAppendStream(), Optional.empty(), "");

    verifyRecordCounts(1, dumpRawTableRecords(getStreamId()), 1, dumpFinalTableRecords(getStreamId(), ""));
  }

  @Override
  @Test
  public void incrementalDedupNoCursor() throws Exception {
    var streamConfig = new StreamConfig(getStreamId(), DestinationSyncMode.APPEND_DEDUP, getPrimaryKey(), Optional.empty(), getCOLUMNS(), 0, 0, 0);
    createRawTable(getStreamId());
    createFinalTable(streamConfig, "");
    insertRawTableRecords(getStreamId(),
        java.util.List.of(Jsons.deserialize("""
                                            {
                                              "_airbyte_raw_id": "c5bcae50-962e-4b92-b2eb-1659eae31693",
                                              "_airbyte_extracted_at": "2023-01-01T00:00:00",
                                              "_airbyte_data": {
                                                "id1": 1,
                                                "id2": 100,
                                                "string": "foo"
                                              }
                                            }
                                            """), Jsons.deserialize("""
                                                                    {
                                                                      "_airbyte_raw_id": "93f1bdd8-1916-4e6c-94dc-29a5d9701179",
                                                                      "_airbyte_extracted_at": "2023-01-01T01:00:00",
                                                                      "_airbyte_data": {
                                                                        "id1": 1,
                                                                        "id2": 100,
                                                                        "string": "bar"
                                                                      }
                                                                    }
                                                                    """)));

    executeTypeAndDedupe(getSqlGenerator(), getDestinationHandler(), streamConfig, Optional.empty(), "");

    var actualRawRecords = dumpRawTableRecords(getStreamId());
    var actualFinalRecords = dumpFinalTableRecords(getStreamId(), "");
    verifyRecordCounts(2, actualRawRecords, 1, actualFinalRecords);
    Assertions.assertEquals("bar", actualFinalRecords.get(0).get(getGenerator().buildColumnId("string").getName()).asText());
  }

  @ParameterizedTest
  @ValueSource(strings = {"$", "${", "${${", "${foo}", "\"", "'", "`", ".", "$$", "\\", "{", "}"})
  @Override
  public void noCrashOnSpecialCharacters(@NotNull String specialChars) throws Exception {

    var str = specialChars + "_" + getNamespace() + "_" + specialChars;
    var originalStreamId = getGenerator().buildStreamId(str, str, "unused");
    var modifiedStreamId = buildStreamId(originalStreamId.getFinalNamespace(), originalStreamId.getFinalName(), "raw_table");
    var columnId = getGenerator().buildColumnId(str);
    try {
      createNamespace(modifiedStreamId.getFinalNamespace());
      createRawTable(modifiedStreamId);
      insertRawTableRecords(modifiedStreamId, java.util.List.of(Jsons.jsonNode(java.util.Map.of("_airbyte_raw_id",
          "758989f2-b148-4dd3-8754-30d9c17d05fb", "_airbyte_extracted_at", "2023-01-01T00:00:00", "_airbyte_data", java.util.Map.of(str, "bar")))));
      LinkedHashMap<ColumnId, AirbyteType> columns = new LinkedHashMap<>();
      columns.put(columnId, AirbyteProtocolType.STRING);
      var stream =
          new StreamConfig(modifiedStreamId, DestinationSyncMode.APPEND_DEDUP, java.util.List.of(columnId), Optional.of(columnId), columns, 0, 0, 0);

      var createTable = getGenerator().createTable(stream, "", false);
      getDestinationHandler().execute(createTable);
      // Not verifying anything about the data; let's just make sure we don't crash.
      executeTypeAndDedupe(getGenerator(), getDestinationHandler(), stream, Optional.empty(), "");
    } finally {
      teardownNamespace(modifiedStreamId.getFinalNamespace());
    }
  }

  @Override
  @Test
  public void incrementalDedupSameNameNamespace() throws Exception {
    var streamId = buildStreamId(getNamespace(), getNamespace(), getNamespace() + "_raw");
    var stream = new StreamConfig(streamId, DestinationSyncMode.APPEND_DEDUP, getIncrementalDedupStream().getPrimaryKey(),
        getIncrementalDedupStream().getCursor(), getIncrementalDedupStream().getColumns(), 0, 0, 0);

    createRawTable(streamId);
    createFinalTable(stream, "");
    insertRawTableRecords(streamId, java.util.List.of(Jsons.deserialize("""
                                                                        {
                                                                          "_airbyte_raw_id": "5ce60e70-98aa-4fe3-8159-67207352c4f0",
                                                                          "_airbyte_extracted_at": "2023-01-01T00:00:00",
                                                                          "_airbyte_data": {"id1": 1, "id2": 100}
                                                                        }
                                                                        """)));

    executeTypeAndDedupe(getGenerator(), getDestinationHandler(), stream, Optional.empty(), "");

    var rawRecords = dumpRawTableRecords(streamId);
    var finalRecords = dumpFinalTableRecords(streamId, "");
    verifyRecordCounts(1, rawRecords, 1, finalRecords);
  }

  @Test
  public void noColumns() throws Exception {
    createRawTable(getStreamId());
    insertRawTableRecords(getStreamId(), java.util.List.of(Jsons.deserialize("""
                                                                             {
                                                                               "_airbyte_raw_id": "14ba7c7f-e398-4e69-ac22-28d578400dbc",
                                                                               "_airbyte_extracted_at": "2023-01-01T00:00:00",
                                                                               "_airbyte_data": {}
                                                                             }
                                                                             """)));
    var stream =
        new StreamConfig(getStreamId(), DestinationSyncMode.APPEND, Collections.emptyList(), Optional.empty(), new LinkedHashMap<>(), 0, 0, 0);
    var createTable = getGenerator().createTable(stream, "", false);
    getDestinationHandler().execute(createTable);
    executeTypeAndDedupe(getGenerator(), getDestinationHandler(), stream, Optional.empty(), "");
    verifyRecords("sqlgenerator/nocolumns_expectedrecords_raw.jsonl", dumpRawTableRecords(getStreamId()),
        "sqlgenerator/nocolumns_expectedrecords_final.jsonl", dumpFinalTableRecords(getStreamId(), ""));
  }

  @Disabled
  @Test
  @Override
  public void testV1V2migration() throws Exception {
    super.testV1V2migration();
  }

  @Override
  @Test
  public void ignoreOldRawRecords() throws Exception {
    createRawTable(getStreamId());
    createFinalTable(getIncrementalAppendStream(), "");
    insertRawTableRecords(getStreamId(),
        java.util.List.of(Jsons.deserialize("""
                                            {
                                              "_airbyte_raw_id": "c5bcae50-962e-4b92-b2eb-1659eae31693",
                                              "_airbyte_extracted_at": "2022-01-01T00:00:00",
                                              "_airbyte_data": {
                                                "string": "foo"
                                              }
                                            }
                                            """), Jsons.deserialize("""
                                                                    {
                                                                      "_airbyte_raw_id": "93f1bdd8-1916-4e6c-94dc-29a5d9701179",
                                                                      "_airbyte_extracted_at": "2023-01-01T01:00:00",
                                                                      "_airbyte_data": {
                                                                        "string": "bar"
                                                                      }
                                                                    }
                                                                    """)));
    executeTypeAndDedupe(getGenerator(), getDestinationHandler(), getIncrementalAppendStream(), Optional.of(Instant.parse("2023-01-01T00:00:00Z")),
        "");
    var rawRecords = dumpRawTableRecords(getStreamId());
    var finalRecords = dumpFinalTableRecords(getStreamId(), "");
    Assertions.assertAll(
        () -> Assertions.assertEquals(1, rawRecords.stream().filter(n -> n.get("_airbyte_loaded_at") == null).count(),
            "Raw table should only have non-null loaded_at on the newer record"),
        () -> Assertions.assertEquals(1, finalRecords.size(), "T+D should only execute on the newer record"));
  }

  @Override
  @Test
  public void cdcImmediateDeletion() throws Exception {
    createRawTable(getStreamId());
    createFinalTable(getCdcIncrementalDedupStream(), "");
    insertRawTableRecords(getStreamId(), List.of(Jsons.deserialize("""
                                                                   {
                                                                     "_airbyte_raw_id": "4fa4efe2-3097-4464-bd22-11211cc3e15b",
                                                                     "_airbyte_extracted_at": "2023-01-01T00:00:00",
                                                                     "_airbyte_data": {
                                                                       "id1": 1,
                                                                       "id2": 100,
                                                                       "updated_at": "2023-01-01T00:00:00",
                                                                       "_ab_cdc_deleted_at": "2023-01-01T00:01:00"
                                                                     }
                                                                   }

                                                                   """)));
    executeTypeAndDedupe(getGenerator(), getDestinationHandler(), getCdcIncrementalDedupStream(), Optional.empty(), "");
    verifyRecordCounts(1, dumpRawTableRecords(getStreamId()), 0, dumpFinalTableRecords(getStreamId(), ""));
  }

  @Override
  @Test
  public void overwriteFinalTable() throws Exception {
    createFinalTable(getIncrementalAppendStream(), "_tmp");
    var records = List.of(Jsons.deserialize("""
                                            {
                                              "_airbyte_raw_id": "4fa4efe2-3097-4464-bd22-11211cc3e15b",
                                              "_airbyte_extracted_at": "2023-01-01T00:00:00",
                                              "_airbyte_meta": {}
                                            }

                                            """));
    insertFinalTableRecords(false, getStreamId(), "_tmp", records, 0);

    var sql = getGenerator().overwriteFinalTable(getStreamId(), "_tmp");
    getDestinationHandler().execute(sql);
    Assertions.assertEquals(1, dumpFinalTableRecords(getStreamId(), "").size());
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
                    .withJsonSchema(Jsons.jsonNode(Map.of("type", "object", "properties",
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
      insertRawTableRecords(streamId, List.of(Jsons.jsonNode(Map.of("_airbyte_raw_id", "ad3e8c84-e02e-4df4-b146-3d5a007b21b4",
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

  @Override
  @Test
  public void minTimestampBehavesCorrectly() throws Exception {
    // When the raw table doesn't exist, there are no unprocessed records and no timestamp
    Assertions.assertEquals(new InitialRawTableStatus(false, false, Optional.empty()), getInitialRawTableState(getIncrementalAppendStream()));

    // When the raw table is empty, there are still no unprocessed records and no timestamp
    createRawTable(getStreamId());
    Assertions.assertEquals(new InitialRawTableStatus(true, false, Optional.empty()), getInitialRawTableState(getIncrementalAppendStream()));

    // If we insert some raw records with null loaded_at, we should get the min extracted_at
    insertRawTableRecords(getStreamId(),
        java.util.List.of(Jsons.deserialize("""
                                            {
                                              "_airbyte_raw_id": "899d3bc3-7921-44f0-8517-c748a28fe338",
                                              "_airbyte_extracted_at": "2023-01-01T00:00:00",
                                              "_airbyte_data": {}
                                            }

                                            """), Jsons.deserialize("""
                                                                    {
                                                                      "_airbyte_raw_id": "47f46eb6-fcae-469c-a7fc-31d4b9ce7474",
                                                                      "_airbyte_extracted_at": "2023-01-02T00:00:00",
                                                                      "_airbyte_data": {}
                                                                    }

                                                                    """)));
    var tableState = getInitialRawTableState(getIncrementalAppendStream());
    Assertions.assertTrue(tableState.getHasUnprocessedRecords(),
        "When all raw records have null loaded_at, we should recognize that there are unprocessed records");
    Assertions.assertTrue(tableState.getMaxProcessedTimestamp().get().isBefore(Instant.parse("2023-01-01T00:00:00z")),
        "When all raw records have null loaded_at, the min timestamp should be earlier than all of their extracted_at values (2023-01-01). Was actually "
            + tableState.getMaxProcessedTimestamp().get());

    // Execute T+D to set loaded_at on the records
    createFinalTable(getIncrementalAppendStream(), "");
    executeTypeAndDedupe(getGenerator(), getDestinationHandler(), getIncrementalAppendStream(), Optional.empty(), "");

    Assertions.assertEquals(getInitialRawTableState(getIncrementalAppendStream()),
        new InitialRawTableStatus(true, false, Optional.of(Instant.parse("2023-01-02T00:00:00Z"))),
        "When all raw records have non-null loaded_at, we should recognize that there are no unprocessed records, and the min timestamp should be equal to the latest extracted_at");

    insertRawTableRecords(getStreamId(), java.util.List.of(Jsons.deserialize("""
                                                                             {
                                                                               "_airbyte_raw_id": "899d3bc3-7921-44f0-8517-c748a28fe338",
                                                                               "_airbyte_extracted_at": "2023-01-01T12:00:00",
                                                                               "_airbyte_data": {}
                                                                             }

                                                                             """)));
    tableState = getInitialRawTableState(getIncrementalAppendStream());
    Assertions.assertTrue(tableState.getHasUnprocessedRecords(),
        "When some raw records have null loaded_at, we should recognize that there are unprocessed records");
    Assertions.assertTrue(tableState.getMaxProcessedTimestamp().get().isBefore(Instant.parse("2023-01-01T12:00:00Z")),
        "When some raw records have null loaded_at, the min timestamp should be earlier than the oldest unloaded record (2023-01-01 12:00Z). Was actually "
            + tableState);
    assertFalse(tableState.getMaxProcessedTimestamp().get().isBefore(Instant.parse("2023-01-01T00:00:00Z")),
        "When some raw records have null loaded_at, the min timestamp should be later than the newest loaded record older than the oldest unloaded record (2023-01-01 00:00Z). Was actually "
            + tableState);
  }

  @AfterAll
  public static void teardownSingleStore() {
    testContainer.close();
  }

  @Override
  protected void teardownNamespace(@NotNull String namespace) throws Exception {
    database.execute(getDslContext().dropSchema(namespace).getSQL(ParamType.INLINED));
  }

  @Override
  protected JdbcDatabase getDatabase() {
    return database;
  }

  @Override
  protected DataType<?> getStructType() {
    return JSON_TYPE;
  }

  @Override
  protected JdbcSqlGenerator getSqlGenerator() {
    return new SingleStoreSqlGenerator(new SingleStoreNameTransformer(), config);
  }

  @Override
  protected SingleStoreDestinationHandler getDestinationHandler() {
    return new SingleStoreDestinationHandler(databaseName, database, getNamespace());
  }

  @Override
  protected SQLDialect getSqlDialect() {
    return SQLDialect.MYSQL;
  }

  @Override
  protected Field<?> toJsonValue(final String valueAsString) {
    return DslUtils.cast(DSL.val(valueAsString), JSON_TYPE, true);
  }

  @Test
  @Override
  public void testCreateTableIncremental() throws Exception {
    var config = getIncrementalDedupStream();
    final Sql sql = getGenerator().createTable(config, "", false);
    getDestinationHandler().execute(sql);
    List<DestinationInitialStatus<MinimumDestinationState>> initialStatuses = getDestinationHandler().gatherInitialState(List.of(config));
    assertEquals(1, initialStatuses.size());
    final DestinationInitialStatus<MinimumDestinationState> initialStatus = initialStatuses.getFirst();
    assertTrue(initialStatus.isFinalTablePresent());
    assertFalse(initialStatus.isSchemaMismatch());
  }

}
