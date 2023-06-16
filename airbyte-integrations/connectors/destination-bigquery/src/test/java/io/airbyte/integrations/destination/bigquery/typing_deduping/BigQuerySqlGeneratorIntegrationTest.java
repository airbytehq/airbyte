package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static com.google.cloud.bigquery.LegacySQLTypeName.legacySQLTypeName;
import static io.airbyte.integrations.destination.bigquery.BigQueryDestination.getServiceAccountCredentials;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.Field;
import com.google.cloud.bigquery.Field.Mode;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.Schema;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.Table;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.AirbyteProtocolType;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Struct;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.ParsedType;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.StreamConfig;
import io.airbyte.integrations.destination.bigquery.typing_deduping.SqlGenerator.ColumnId;
import io.airbyte.integrations.destination.bigquery.typing_deduping.SqlGenerator.StreamId;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;
import org.apache.commons.text.StringSubstitutor;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// TODO this proooobably belongs in test-integration?
// TODO can we run these test methods in parallel? They're each writing to a different namespace, so there's no risk of stomping anything.
public class BigQuerySqlGeneratorIntegrationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQuerySqlGeneratorIntegrationTest.class);
  private final static BigQuerySqlGenerator GENERATOR = new BigQuerySqlGenerator();
  public static final ColumnId CURSOR = GENERATOR.buildColumnId("updated_at");
  public static final List<ColumnId> PRIMARY_KEY = List.of(GENERATOR.buildColumnId("id"));
  public static final String QUOTE = "`";

  private static BigQuery bq;
  private static LinkedHashMap<ColumnId, ParsedType<StandardSQLTypeName>> columns;
  private static LinkedHashMap<ColumnId, ParsedType<StandardSQLTypeName>> cdcColumns;

  private String testDataset;
  private StreamId streamId;

  @BeforeAll
  public static void setup() throws Exception {
    String rawConfig = Files.readString(Path.of("secrets/credentials-gcs-staging.json"));
    JsonNode config = Jsons.deserialize(rawConfig);

    final BigQueryOptions.Builder bigQueryBuilder = BigQueryOptions.newBuilder();
    final GoogleCredentials credentials = getServiceAccountCredentials(config);
    bq = bigQueryBuilder
        .setProjectId(config.get("project_id").asText())
        .setCredentials(credentials)
        .setHeaderProvider(BigQueryUtils.getHeaderProvider())
        .build()
        .getService();

    columns = new LinkedHashMap<>();
    columns.put(GENERATOR.buildColumnId("id"), new ParsedType<>(StandardSQLTypeName.INT64, AirbyteProtocolType.INTEGER));
    columns.put(GENERATOR.buildColumnId("updated_at"), new ParsedType<>(StandardSQLTypeName.TIMESTAMP, AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE));
    columns.put(GENERATOR.buildColumnId("name"), new ParsedType<>(StandardSQLTypeName.STRING, AirbyteProtocolType.STRING));

    LinkedHashMap<String, AirbyteType> addressProperties = new LinkedHashMap<>();
    addressProperties.put("city", AirbyteProtocolType.STRING);
    addressProperties.put("state", AirbyteProtocolType.STRING);
    columns.put(GENERATOR.buildColumnId("address"), new ParsedType<>(StandardSQLTypeName.JSON, new Struct(addressProperties)));

    columns.put(GENERATOR.buildColumnId("age"), new ParsedType<>(StandardSQLTypeName.INT64, AirbyteProtocolType.INTEGER));

    cdcColumns = new LinkedHashMap<>();
    cdcColumns.put(GENERATOR.buildColumnId("id"), new ParsedType<>(StandardSQLTypeName.INT64, AirbyteProtocolType.INTEGER));
    cdcColumns.put(GENERATOR.buildColumnId("_ab_cdc_lsn"), new ParsedType<>(StandardSQLTypeName.INT64, AirbyteProtocolType.INTEGER));
    cdcColumns.put(GENERATOR.buildColumnId("_ab_cdc_deleted_at"),
        new ParsedType<>(StandardSQLTypeName.TIMESTAMP, AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE));
    cdcColumns.put(GENERATOR.buildColumnId("name"), new ParsedType<>(StandardSQLTypeName.STRING, AirbyteProtocolType.STRING));
    // This is a bit unrealistic - DB sources don't actually declare explicit properties in their JSONB columns, and JSONB isn't necessarily a Struct anyway.
    cdcColumns.put(GENERATOR.buildColumnId("address"), new ParsedType<>(StandardSQLTypeName.JSON, new Struct(addressProperties)));
    cdcColumns.put(GENERATOR.buildColumnId("age"), new ParsedType<>(StandardSQLTypeName.INT64, AirbyteProtocolType.INTEGER));
  }

  @BeforeEach
  public void setupDataset() {
    testDataset = "bq_sql_generator_test_" + UUID.randomUUID().toString().replace("-", "_");
    // This is not a typical stream ID would look like, but we're just using this to isolate our tests to a specific dataset.
    // In practice, the final table would be testDataset.users, and the raw table would be airbyte.testDataset_users.
    streamId = new StreamId(testDataset, "users_final", testDataset, "users_raw", testDataset, "users_final");
    LOGGER.info("Running in dataset {}", testDataset);
    bq.create(DatasetInfo.newBuilder(testDataset).build());
  }

  @AfterEach
  public void teardownDataset() {
    bq.delete(testDataset, BigQuery.DatasetDeleteOption.deleteContents());
  }

  @Test
  public void testCreateTableIncremental() throws InterruptedException {
    final String sql = GENERATOR.createTable(incrementalDedupStreamConfig(), "");
    LOGGER.info("Executing sql: {}", sql);
    bq.query(QueryJobConfiguration.newBuilder(sql).build());

    final Table table = bq.getTable(testDataset, "users_final");
    // The table should exist
    assertNotNull(table);
    final Schema schema = table.getDefinition().getSchema();
    // And we should know exactly what columns it contains
    assertEquals(
        // Would be nice to assert directly against StandardSQLTypeName, but bigquery returns schemas of LegacySQLTypeName. So we have to translate.
        Schema.of(
            Field.newBuilder("_airbyte_raw_id", legacySQLTypeName(StandardSQLTypeName.STRING)).setMode(Mode.REQUIRED).build(),
            Field.newBuilder("_airbyte_extracted_at", legacySQLTypeName(StandardSQLTypeName.TIMESTAMP)).setMode(Mode.REQUIRED).build(),
            Field.newBuilder("_airbyte_meta", legacySQLTypeName(StandardSQLTypeName.JSON)).setMode(Mode.REQUIRED).build(),
            Field.of("id", legacySQLTypeName(StandardSQLTypeName.INT64)),
            Field.of("updated_at", legacySQLTypeName(StandardSQLTypeName.TIMESTAMP)),
            Field.of("name", legacySQLTypeName(StandardSQLTypeName.STRING)),
            Field.of("address", legacySQLTypeName(StandardSQLTypeName.JSON)),
            Field.of("age", legacySQLTypeName(StandardSQLTypeName.INT64))
        ),
        schema
    );
    // TODO this should assert partitioning/clustering configs
  }

  @Test
  public void testVerifyPrimaryKeysIncremental() throws InterruptedException {
    createRawTable();
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "dataset", testDataset
        )).replace("""
            INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
              (JSON'{}', '10d6e27d-ae7a-41b5-baf8-c4c277ef9c11', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 1}', '5ce60e70-98aa-4fe3-8159-67207352c4f0', '2023-01-01T00:00:00Z');
            """)
    ).build());

    // This variable is declared outside of the transaction, so we need to do it manually here
    final String sql = "DECLARE missing_pk_count INT64;" + GENERATOR.validatePrimaryKeys(streamId, List.of(new ColumnId("id", "id", "id")), columns);
    LOGGER.info("Executing sql: {}", sql);
    final BigQueryException e = assertThrows(
        BigQueryException.class,
        () -> bq.query(QueryJobConfiguration.newBuilder(sql).build())
    );

    assertTrue(e.getError().getMessage().startsWith("Raw table has 1 rows missing a primary key at"),
        "Message was actually: " + e.getError().getMessage());
  }

  @Test
  public void testInsertNewRecordsIncremental() throws InterruptedException {
    createRawTable();
    createFinalTable();
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "dataset", testDataset
        )).replace("""
            INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
              (JSON'{"id": 1, "name": "Alice", "address": {"city": "San Francisco", "state": "CA"}, "updated_at": "2023-01-01T01:00:00Z"}', '972fa08a-aa06-4b91-a6af-a371aee4cb1c', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 1, "name": "Alice", "address": {"city": "San Diego", "state": "CA"}, "updated_at": "2023-01-01T02:00:00Z"}', '233ad43d-de50-4a47-bbe6-7a417ce60d9d', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 2, "name": "Bob", "age": "oops", "updated_at": "2023-01-01T03:00:00Z"}', 'd4aeb036-2d95-4880-acd2-dc69b42b03c6', '2023-01-01T00:00:00Z');
            """)
    ).build());

    final String sql = GENERATOR.insertNewRecords(streamId, "", columns);
    LOGGER.info("Executing sql: {}", sql);
    bq.query(QueryJobConfiguration.newBuilder(sql).build());

    // TODO more stringent asserts
    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId(QUOTE)).build()).getTotalRows();
    assertEquals(3, finalRows);
  }

  @Test
  public void testDedupFinalTable() throws InterruptedException {
    createRawTable();
    createFinalTable();
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "dataset", testDataset
        )).replace("""
            INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
              (JSON'{"id": 1, "name": "Alice", "address": {"city": "San Francisco", "state": "CA"}, "age": 42, "updated_at": "2023-01-01T01:00:00Z"}', 'd7b81af0-01da-4846-a650-cc398986bc99', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 1, "name": "Alice", "address": {"city": "San Diego", "state": "CA"}, "age": 84, "updated_at": "2023-01-01T02:00:00Z"}', '80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 2, "name": "Bob", "age": "oops", "updated_at": "2023-01-01T03:00:00Z"}', 'ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z');
                        
            INSERT INTO ${dataset}.users_final (_airbyte_raw_id, _airbyte_extracted_at, _airbyte_meta, id, updated_at, name, address, age) values
              ('d7b81af0-01da-4846-a650-cc398986bc99', '2023-01-01T00:00:00Z', JSON'{"errors":[]}', 1, '2023-01-01T01:00:00Z', 'Alice', JSON'{"city": "San Francisco", "state": "CA"}', 42),
              ('80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z', JSON'{"errors":[]}', 1, '2023-01-01T02:00:00Z', 'Alice', JSON'{"city": "San Diego", "state": "CA"}', 84),
              ('ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z', JSON'{"errors": ["blah blah age"]}', 2, '2023-01-01T03:00:00Z', 'Bob', NULL, NULL);
            """)
    ).build());

    final String sql = GENERATOR.dedupFinalTable(streamId, "", PRIMARY_KEY, CURSOR, columns);
    LOGGER.info("Executing sql: {}", sql);
    bq.query(QueryJobConfiguration.newBuilder(sql).build());

    // TODO more stringent asserts
    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId(QUOTE)).build()).getTotalRows();
    assertEquals(2, finalRows);
  }

  @Test
  public void testDedupRawTable() throws InterruptedException {
    createRawTable();
    createFinalTable();
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "dataset", testDataset
        )).replace("""
            INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
              (JSON'{"id": 1, "name": "Alice", "address": {"city": "San Francisco", "state": "CA"}, "age": 42, "updated_at": "2023-01-01T01:00:00Z"}', 'd7b81af0-01da-4846-a650-cc398986bc99', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 1, "name": "Alice", "address": {"city": "San Diego", "state": "CA"}, "age": 84, "updated_at": "2023-01-01T02:00:00Z"}', '80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 2, "name": "Bob", "age": "oops", "updated_at": "2023-01-01T03:00:00Z"}', 'ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z');
                        
            INSERT INTO ${dataset}.users_final (_airbyte_raw_id, _airbyte_extracted_at, _airbyte_meta, id, updated_at, name, address, age) values
              ('80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z', JSON'{"errors":[]}', 1, '2023-01-01T02:00:00Z', 'Alice', JSON'{"city": "San Diego", "state": "CA"}', 84),
              ('ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z', JSON'{"errors": ["blah blah age"]}', 2, '2023-01-01T03:00:00Z', 'Bob', NULL, NULL);
            """)
    ).build());

    final String sql = GENERATOR.dedupRawTable(streamId, "");
    LOGGER.info("Executing sql: {}", sql);
    bq.query(QueryJobConfiguration.newBuilder(sql).build());

    // TODO more stringent asserts
    final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
    assertEquals(2, rawRows);
  }

  @Test
  public void testCommitRawTable() throws InterruptedException {
    createRawTable();
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "dataset", testDataset
        )).replace("""
            INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
              (JSON'{"id": 1, "name": "Alice", "address": {"city": "San Diego", "state": "CA"}, "age": 84, "updated_at": "2023-01-01T02:00:00Z"}', '80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 2, "name": "Bob", "age": "oops", "updated_at": "2023-01-01T03:00:00Z"}', 'ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z');
            """)
    ).build());

    final String sql = GENERATOR.commitRawTable(streamId);
    LOGGER.info("Executing sql: {}", sql);
    bq.query(QueryJobConfiguration.newBuilder(sql).build());

    // TODO more stringent asserts
    final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
        "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
    assertEquals(0, rawUntypedRows);
  }

  // TODO some of these test cases don't actually need a suffix. Figure out which ones make sense and which ones don't.
  @Test
  public void testFullUpdateIncrementalDedup() throws InterruptedException {
    createRawTable();
    createFinalTable("_foo");
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "dataset", testDataset
        )).replace("""
            INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
              (JSON'{"id": 1, "name": "Alice", "address": {"city": "San Francisco", "state": "CA"}, "age": 42, "updated_at": "2023-01-01T01:00:00Z"}', 'd7b81af0-01da-4846-a650-cc398986bc99', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 1, "name": "Alice", "address": {"city": "San Diego", "state": "CA"}, "age": 84, "updated_at": "2023-01-01T02:00:00Z"}', '80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 2, "name": "Bob", "age": "oops", "updated_at": "2023-01-01T03:00:00Z"}', 'ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z');
            """)
    ).build());

    final String sql = GENERATOR.updateTable("_foo", incrementalDedupStreamConfig());
    LOGGER.info("Executing sql: {}", sql);
    bq.query(QueryJobConfiguration.newBuilder(sql).build());

    // TODO
    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId("_foo", QUOTE)).build()).getTotalRows();
    assertEquals(2, finalRows);
    final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
    assertEquals(2, rawRows);
    final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
        "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
    assertEquals(0, rawUntypedRows);
  }

  @Test
  public void testFullUpdateIncrementalAppend() throws InterruptedException {
    createRawTable();
    createFinalTable("_foo");
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "dataset", testDataset
        )).replace("""
            INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
              (JSON'{"id": 1, "name": "Alice", "address": {"city": "San Francisco", "state": "CA"}, "age": 42, "updated_at": "2023-01-01T01:00:00Z"}', 'd7b81af0-01da-4846-a650-cc398986bc99', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 1, "name": "Alice", "address": {"city": "San Diego", "state": "CA"}, "age": 84, "updated_at": "2023-01-01T02:00:00Z"}', '80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 2, "name": "Bob", "age": "oops", "updated_at": "2023-01-01T03:00:00Z"}', 'ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z');
            """)
    ).build());

    final String sql = GENERATOR.updateTable("_foo", incrementalAppendStreamConfig());
    LOGGER.info("Executing sql: {}", sql);
    bq.query(QueryJobConfiguration.newBuilder(sql).build());

    // TODO
    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId("_foo", QUOTE)).build()).getTotalRows();
    assertEquals(3, finalRows);
    final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
    assertEquals(3, rawRows);
    final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
        "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
    assertEquals(0, rawUntypedRows);
  }

  // This is also effectively the full refresh overwrite test case.
  // In the overwrite case, we rely on the destination connector to tell us to write to a final table with a _tmp suffix, and then call overwriteFinalTable at the end of the sync.
  @Test
  public void testFullUpdateFullRefreshAppend() throws InterruptedException {
    createRawTable();
    createFinalTable("_foo");
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "dataset", testDataset
        )).replace("""
            INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
              (JSON'{"id": 1, "name": "Alice", "address": {"city": "San Francisco", "state": "CA"}, "age": 42, "updated_at": "2023-01-01T01:00:00Z"}', 'd7b81af0-01da-4846-a650-cc398986bc99', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 1, "name": "Alice", "address": {"city": "San Diego", "state": "CA"}, "age": 84, "updated_at": "2023-01-01T02:00:00Z"}', '80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 2, "name": "Bob", "age": "oops", "updated_at": "2023-01-01T03:00:00Z"}', 'ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z');
                        
            INSERT INTO ${dataset}.users_final_foo (_airbyte_raw_id, _airbyte_extracted_at, _airbyte_meta, id, updated_at, name, address, age) values
              ('64f4390f-3da1-4b65-b64a-a6c67497f18d', '2022-12-31T00:00:00Z', JSON'{"errors": []}', 1, '2022-12-31T00:00:00Z', 'Alice', NULL, NULL);
            """)
    ).build());

    final String sql = GENERATOR.updateTable("_foo", fullRefreshAppendStreamConfig());
    LOGGER.info("Executing sql: {}", sql);
    bq.query(QueryJobConfiguration.newBuilder(sql).build());

    // TODO
    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId("_foo", QUOTE)).build()).getTotalRows();
    assertEquals(4, finalRows);
    final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
    assertEquals(3, rawRows);
    final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
        "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
    assertEquals(0, rawUntypedRows);
  }

  @Test
  public void testRenameFinalTable() throws InterruptedException {
    createFinalTable("_tmp");

    final String sql = GENERATOR.overwriteFinalTable("_tmp", fullRefreshOverwriteStreamConfig()).get();
    LOGGER.info("Executing sql: {}", sql);
    bq.query(QueryJobConfiguration.newBuilder(sql).build());

    final Table table = bq.getTable(testDataset, "users_final");
    // TODO this should assert table schema + partitioning/clustering configs
    assertNotNull(table);
  }

  @Test
  public void testCdcUpdate() throws InterruptedException {
    createRawTable();
    createFinalTableCdc();
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "dataset", testDataset
        )).replace("""
            -- records from a previous sync
            INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`, `_airbyte_loaded_at`) VALUES
              (JSON'{"id": 1, "_ab_cdc_lsn": 10000, "name": "spooky ghost"}', '64f4390f-3da1-4b65-b64a-a6c67497f18d', '2022-12-31T00:00:00Z', '2022-12-31T00:00:01Z');
            INSERT INTO ${dataset}.users_final (_airbyte_raw_id, _airbyte_extracted_at, _airbyte_meta, id, _ab_cdc_lsn, name, address, age) values
              ('64f4390f-3da1-4b65-b64a-a6c67497f18d', '2022-12-31T00:00:00Z', JSON'{}', 1, 1000, 'spooky ghost', NULL, NULL);
                        
            -- new records from the current sync
            INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
              (JSON'{"id": 2, "name": "Alice", "address": {"city": "San Francisco", "state": "CA"}, "age": 42, "_ab_cdc_lsn": 10001}', 'd7b81af0-01da-4846-a650-cc398986bc99', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 2, "name": "Alice", "address": {"city": "San Diego", "state": "CA"}, "age": 84, "_ab_cdc_lsn": 10002}', '80c99b54-54b4-43bd-b51b-1f67dafa2c52', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 3, "name": "Bob", "age": "oops", "_ab_cdc_lsn": 10003}', 'ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z'),
              (JSON'{"id": 1, "_ab_cdc_lsn": 10004, "_ab_cdc_deleted_at": "2022-12-31T23:59:59Z"}', 'ad690bfb-c2c2-4172-bd73-a16c86ccbb67', '2023-01-01T00:00:00Z');
            """)
    ).build());

    final String sql = GENERATOR.updateTable("", cdcStreamConfig());
    LOGGER.info("Executing sql: {}", sql);
    bq.query(QueryJobConfiguration.newBuilder(sql).build());

    // TODO
    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId("", QUOTE)).build()).getTotalRows();
    assertEquals(2, finalRows);
    final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
    assertEquals(3, rawRows);
    final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
        "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
    assertEquals(0, rawUntypedRows);
  }

  /**
   * source operations:
   * <ol>
   *   <li>insert id=1 (lsn 10000)</li>
   *   <li>delete id=1 (lsn 10001)</li>
   * </ol>
   * <p>
   * But the destination writes lsn 10001 before 10000. We should still end up with no records in the final table.
   * <p>
   * All records have the same emitted_at timestamp. This means that we live or die purely based on our ability to use _ab_cdc_lsn.
   */
  @Test
  public void testCdcOrdering_updateAfterDelete() throws InterruptedException {
    createRawTable();
    createFinalTableCdc();
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "dataset", testDataset
        )).replace("""
            -- Write raw deletion record from the first batch, which resulted in an empty final table.
            -- Note the non-null loaded_at - this is to simulate that we previously ran T+D on this record.
            INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`, `_airbyte_loaded_at`) VALUES
              (JSON'{"id": 1, "_ab_cdc_lsn": 10001, "_ab_cdc_deleted_at": "2023-01-01T00:01:00Z"}', generate_uuid(), '2023-01-01T00:00:00Z', '2023-01-01T00:00:01Z');
              
            -- insert raw record from the second record batch - this is an outdated record that should be ignored.
            INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
              (JSON'{"id": 1, "_ab_cdc_lsn": 10001, "name": "alice"}', generate_uuid(), '2023-01-01T00:00:00Z');
            """)
    ).build());

    final String sql = GENERATOR.updateTable("", cdcStreamConfig());
    LOGGER.info("Executing sql: {}", sql);
    bq.query(QueryJobConfiguration.newBuilder(sql).build());

    // TODO better asserts
    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId("", QUOTE)).build()).getTotalRows();
    assertEquals(0, finalRows);
    final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
    assertEquals(1, rawRows);
    final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
        "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
    assertEquals(0, rawUntypedRows);
  }

  /**
   * source operations:
   * <ol>
   *   <li>arbitrary history...</li>
   *   <li>delete id=1 (lsn 10001)</li>
   *   <li>reinsert id=1 (lsn 10002)</li>
   * </ol>
   * <p>
   * But the destination receives LSNs 10002 before 10001. In this case, we should keep the reinserted record in the final table.
   * <p>
   * All records have the same emitted_at timestamp. This means that we live or die purely based on our ability to use _ab_cdc_lsn.
   */
  @Test
  public void testCdcOrdering_insertAfterDelete() throws InterruptedException {
    createRawTable();
    createFinalTableCdc();
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "dataset", testDataset
        )).replace("""
            -- records from the first batch
            INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`, `_airbyte_loaded_at`) VALUES
              (JSON'{"id": 1, "_ab_cdc_lsn": 10002, "name": "alice_reinsert"}', '64f4390f-3da1-4b65-b64a-a6c67497f18d', '2023-01-01T00:00:00Z', '2023-01-01T00:00:01Z');
            INSERT INTO ${dataset}.users_final (_airbyte_raw_id, _airbyte_extracted_at, _airbyte_meta, id, _ab_cdc_lsn, name) values
              ('64f4390f-3da1-4b65-b64a-a6c67497f18d', '2023-01-01T00:00:00Z', JSON'{}', 1, 10002, 'alice_reinsert');
            
            -- second record batch
            INSERT INTO ${dataset}.users_raw (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES
              (JSON'{"id": 1, "_ab_cdc_lsn": 10001, "_ab_cdc_deleted_at": "2023-01-01T00:01:00Z"}', generate_uuid(), '2023-01-01T00:00:00Z');
            """)
    ).build());
      // Run the second round of typing and deduping. This should do nothing to the final table, because the delete is outdated.
      final String sql = GENERATOR.updateTable("", cdcStreamConfig());
      LOGGER.info("Executing sql: {}", sql);
      bq.query(QueryJobConfiguration.newBuilder(sql).build());

      final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId("", QUOTE)).build()).getTotalRows();
      assertEquals(1, finalRows);
      final long rawRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.rawTableId(QUOTE)).build()).getTotalRows();
      // TODO assert that the raw record is the alice_reinsert record
      assertEquals(1, rawRows);
      final long rawUntypedRows = bq.query(QueryJobConfiguration.newBuilder(
          "SELECT * FROM " + streamId.rawTableId(QUOTE) + " WHERE _airbyte_loaded_at IS NULL").build()).getTotalRows();
      assertEquals(0, rawUntypedRows);
  }

  private StreamConfig<StandardSQLTypeName> incrementalDedupStreamConfig() {
    return new StreamConfig<>(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        PRIMARY_KEY,
        Optional.of(CURSOR),
        columns
    );
  }

  private StreamConfig<StandardSQLTypeName> cdcStreamConfig() {
    return new StreamConfig<>(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        PRIMARY_KEY,
        // Much like the rest of this class - this is purely for test purposes. Real CDC cursors may not be exactly the same as this.
        Optional.of(GENERATOR.buildColumnId("_ab_cdc_lsn")),
        cdcColumns
    );
  }

  private StreamConfig<StandardSQLTypeName> incrementalAppendStreamConfig() {
    return new StreamConfig<>(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND,
        null,
        Optional.of(CURSOR),
        columns
    );
  }

  private StreamConfig<StandardSQLTypeName> fullRefreshAppendStreamConfig() {
    return new StreamConfig<>(
        streamId,
        SyncMode.FULL_REFRESH,
        DestinationSyncMode.APPEND,
        null,
        Optional.empty(),
        columns
    );
  }

  private StreamConfig<StandardSQLTypeName> fullRefreshOverwriteStreamConfig() {
    return new StreamConfig<>(
        streamId,
        SyncMode.FULL_REFRESH,
        DestinationSyncMode.OVERWRITE,
        null,
        Optional.empty(),
        columns
    );
  }

  // These are known-good methods for doing stuff with bigquery.
  // Some of them are identical to what the sql generator does, and that's intentional.
  private void createRawTable() throws InterruptedException {
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "dataset", testDataset
        )).replace("""
            CREATE TABLE ${dataset}.users_raw (
              _airbyte_raw_id STRING NOT NULL,
              _airbyte_data JSON NOT NULL,
              _airbyte_extracted_at TIMESTAMP NOT NULL,
              _airbyte_loaded_at TIMESTAMP
            ) PARTITION BY (
              DATE_TRUNC(_airbyte_extracted_at, DAY)
            ) CLUSTER BY _airbyte_loaded_at;
            """)
    ).build());
  }

  private void createFinalTable() throws InterruptedException {
    createFinalTable("");
  }

  private void createFinalTable(String suffix) throws InterruptedException {
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "dataset", testDataset,
            "suffix", suffix
        )).replace("""
            CREATE TABLE ${dataset}.users_final${suffix} (
              _airbyte_raw_id STRING NOT NULL,
              _airbyte_extracted_at TIMESTAMP NOT NULL,
              _airbyte_meta JSON NOT NULL,
              id INT64,
              updated_at TIMESTAMP,
              name STRING,
              address JSON,
              age INT64
            )
            PARTITION BY (DATE_TRUNC(_airbyte_extracted_at, DAY))
            CLUSTER BY id, _airbyte_extracted_at;
            """)
    ).build());
  }

  private void createFinalTableCdc() throws InterruptedException {
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "dataset", testDataset
        )).replace("""
            CREATE TABLE ${dataset}.users_final (
              _airbyte_raw_id STRING NOT NULL,
              _airbyte_extracted_at TIMESTAMP NOT NULL,
              _airbyte_meta JSON NOT NULL,
              id INT64,
              _ab_cdc_deleted_at TIMESTAMP,
              _ab_cdc_lsn INT64,
              name STRING,
              address JSON,
              age INT64
            )
            PARTITION BY (DATE_TRUNC(_airbyte_extracted_at, DAY))
            CLUSTER BY id, _airbyte_extracted_at;
            """)
    ).build());
  }
}
