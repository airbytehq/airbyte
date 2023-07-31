package io.airbyte.integrations.base.destination.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import org.apache.commons.lang3.tuple.Pair;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.parallel.Execution;
import org.junit.jupiter.api.parallel.ExecutionMode;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Execution(ExecutionMode.CONCURRENT)
public abstract class BaseSqlGeneratorIntegrationTest<DialectTableDefinition> {

  private static final Logger LOGGER = LoggerFactory.getLogger(BaseSqlGeneratorIntegrationTest.class);

  public static final RecordDiffer DIFFER = new RecordDiffer(
      Pair.of("id1", AirbyteProtocolType.INTEGER),
      Pair.of("id2", AirbyteProtocolType.INTEGER),
      Pair.of("updated_at", AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE),
      Pair.of("_ab_cdc_lsn", AirbyteProtocolType.INTEGER)
  );

  private JsonNode config;
  private SqlGenerator<DialectTableDefinition> generator;
  private DestinationHandler<DialectTableDefinition> destinationHandler;
  private ColumnId id1;
  private ColumnId id2;
  private List<ColumnId> primaryKey;
  private ColumnId cursor;
  private ColumnId cdcCursor;
  private LinkedHashMap<ColumnId, AirbyteType> columns;
  private LinkedHashMap<ColumnId, AirbyteType> cdcColumns;
  private String namespace;
  private StreamId streamId;
  private StreamConfig incrementalDedupStream;
  private StreamConfig cdcIncrementalDedupStream;

  protected abstract JsonNode generateConfig() throws Exception;
  protected abstract SqlGenerator<DialectTableDefinition> getSqlGenerator();
  protected abstract DestinationHandler<DialectTableDefinition> getDestinationHandler();
  protected abstract void createNamespace(String namespace);
  protected abstract void createRawTable(StreamId streamId) throws InterruptedException;
  protected abstract void createFinalTable(boolean includeCdcDeletedAt, StreamId streamId, String suffix) throws InterruptedException;
  protected abstract void insertRawTableRecords(StreamId streamId, List<JsonNode> records) throws InterruptedException;
  protected abstract void insertFinalTableRecords(StreamId streamId, String suffix, List<JsonNode> records);
  protected abstract List<JsonNode> dumpRawTableRecords(StreamId streamId) throws Exception;
  protected abstract List<JsonNode> dumpFinalTableRecords(StreamId streamId, String suffix) throws Exception;
  protected abstract void teardownNamespace(String namespace);

  protected JsonNode getConfig() {
    return config;
  }

  @BeforeEach
  public void setup() throws Exception {
    config = generateConfig();

    generator = getSqlGenerator();
    destinationHandler = getDestinationHandler();
    id1 = generator.buildColumnId("id1");
    id2 = generator.buildColumnId("id2");
    primaryKey = List.of(id1, id2);
    cursor = generator.buildColumnId("updated_at");
    cdcCursor = generator.buildColumnId("_ab_cdc_lsn");

    columns = new LinkedHashMap<>();
    columns.put(id1, AirbyteProtocolType.INTEGER);
    columns.put(id2, AirbyteProtocolType.INTEGER);
    columns.put(cursor, AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    columns.put(generator.buildColumnId("struct"), new Struct(new LinkedHashMap<>()));
    columns.put(generator.buildColumnId("array"), new Array(AirbyteProtocolType.UNKNOWN));
    columns.put(generator.buildColumnId("string"), AirbyteProtocolType.STRING);
    columns.put(generator.buildColumnId("number"), AirbyteProtocolType.NUMBER);
    columns.put(generator.buildColumnId("integer"), AirbyteProtocolType.INTEGER);
    columns.put(generator.buildColumnId("boolean"), AirbyteProtocolType.BOOLEAN);
    columns.put(generator.buildColumnId("timestamp_with_timezone"), AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);
    columns.put(generator.buildColumnId("timestamp_without_timezone"), AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE);
    columns.put(generator.buildColumnId("time_with_timezone"), AirbyteProtocolType.TIME_WITH_TIMEZONE);
    columns.put(generator.buildColumnId("time_without_timezone"), AirbyteProtocolType.TIME_WITHOUT_TIMEZONE);
    columns.put(generator.buildColumnId("date"), AirbyteProtocolType.DATE);
    columns.put(generator.buildColumnId("unknown"), AirbyteProtocolType.UNKNOWN);

    cdcColumns = new LinkedHashMap<>(columns);
    cdcColumns.put(generator.buildColumnId("_ab_cdc_deleted_at"), AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE);

    namespace = Strings.addRandomSuffix("sql_generator_test", "_", 5);
    // This is not a typical stream ID would look like, but SqlGenerator isn't allowed to make any
    // assumptions about StreamId structure.
    // In practice, the final table would be testDataset.users, and the raw table would be
    // airbyte_internal.testDataset_ab__ab_users.
    streamId = new StreamId(namespace, "users_final", namespace, "users_raw", namespace, "users_final");

    incrementalDedupStream = new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        primaryKey,
        Optional.of(cursor),
        columns);
    cdcIncrementalDedupStream = new StreamConfig(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        primaryKey,
        Optional.of(cdcCursor),
        cdcColumns);

    LOGGER.info("Running with namespace {}", namespace);
    createNamespace(namespace);
  }

  @AfterEach
  public void teardown() {
    teardownNamespace(namespace);
  }

  @Test
  public void incrementalDedupInvalidPrimaryKey() throws InterruptedException {
    createRawTable(streamId);
    createFinalTable(false, streamId, "");
    insertRawTableRecords(
        streamId,
        List.of(
            Jsons.deserialize(
                """
                    {
                      "_airbyte_raw_id": "10d6e27d-ae7a-41b5-baf8-c4c277ef9c11",
                      "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                      "_airbyte_data": {}
                    }
                    """),
            Jsons.deserialize(
                """
                    {
                      "_airbyte_raw_id": "5ce60e70-98aa-4fe3-8159-67207352c4f0",
                      "_airbyte_extracted_at": "2023-01-01T00:00:00Z",
                      "_airbyte_data": {"id1": 1, "id2": 100}
                    }
                    """)));

    String sql = generator.updateTable(incrementalDedupStream, "");
    assertThrows(
        Exception.class,
        () -> destinationHandler.execute(sql));
  }
}
