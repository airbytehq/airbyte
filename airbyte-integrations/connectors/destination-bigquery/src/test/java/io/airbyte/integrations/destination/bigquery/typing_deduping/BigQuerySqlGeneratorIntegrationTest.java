package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static io.airbyte.integrations.destination.bigquery.BigQueryDestination.getServiceAccountCredentials;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryException;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.DatasetInfo;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.StandardSQLTypeName;
import com.google.cloud.bigquery.Table;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.AirbyteProtocolType;
import io.airbyte.integrations.destination.bigquery.typing_deduping.AirbyteType.Struct;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.ParsedType;
import io.airbyte.integrations.destination.bigquery.typing_deduping.CatalogParser.StreamConfig;
import io.airbyte.integrations.destination.bigquery.typing_deduping.SqlGenerator.QuotedColumnId;
import io.airbyte.integrations.destination.bigquery.typing_deduping.SqlGenerator.QuotedStreamId;
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
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// TODO this proooobably belongs in test-integration?
public class BigQuerySqlGeneratorIntegrationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQuerySqlGeneratorIntegrationTest.class);

  private String testDataset;
  // This is not a typical stream ID would look like, but we're just using this to isolate our tests to a specific dataset.
  // In practice, the final table would be TEST_DATASET.users, and the raw table would be airbyte.TEST_DATASET_users.
  private QuotedStreamId streamId;

  private static BigQuery bq;
  private static BigQuerySqlGenerator generator;
  private static LinkedHashMap<QuotedColumnId, ParsedType<StandardSQLTypeName>> columns;

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

    generator = new BigQuerySqlGenerator();

    columns = new LinkedHashMap<>();
    columns.put(generator.quoteColumnId("id"), new ParsedType<>(StandardSQLTypeName.INT64, AirbyteProtocolType.INTEGER));
    columns.put(generator.quoteColumnId("updated_at"), new ParsedType<>(StandardSQLTypeName.TIMESTAMP, AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE));
    columns.put(generator.quoteColumnId("name"), new ParsedType<>(StandardSQLTypeName.STRING, AirbyteProtocolType.STRING));

    LinkedHashMap<String, AirbyteType> addressProperties = new LinkedHashMap<>();
    addressProperties.put("city", AirbyteProtocolType.STRING);
    addressProperties.put("state", AirbyteProtocolType.STRING);
    columns.put(generator.quoteColumnId("address"), new ParsedType<>(StandardSQLTypeName.STRING, new Struct(addressProperties)));
  }

  @BeforeEach
  public void setupDataset() {
    testDataset = "bq_sql_generator_test_" + UUID.randomUUID().toString().replace("-", "_");
    streamId = new QuotedStreamId(testDataset, "users_final", testDataset, "users_raw", "public", "users");
    LOGGER.info("Running in dataset {}", testDataset);
    bq.create(DatasetInfo.newBuilder(testDataset).build());
  }

  @AfterEach
  public void teardownDataset() {
    bq.delete(testDataset, BigQuery.DatasetDeleteOption.deleteContents());
  }

  @Test
  public void testCreateTableIncremental() throws InterruptedException {
    final String sql = generator.createTable(incrementalDedupStreamConfig());
    bq.query(QueryJobConfiguration.newBuilder(sql).build());

    final Table table = bq.getTable(testDataset, "users");
    assertNotNull(table);
  }

  @Test
  public void testVerifyPrimaryKeysIncremental() throws InterruptedException {
    createRawTable();
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "raw_table_id", streamId.rawTableId()
        )).replace("""
            INSERT INTO ${raw_table_id} (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES (JSON'{}', GENERATE_UUID(), CURRENT_TIMESTAMP());
            INSERT INTO ${raw_table_id} (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES (JSON'{"id": 1}', GENERATE_UUID(), CURRENT_TIMESTAMP());
            """)
    ).build());

    final String sql = generator.validatePrimaryKeys(streamId, List.of(new QuotedColumnId("id", "id")), columns);
    final BigQueryException e = assertThrows(
        BigQueryException.class,
        () -> bq.query(QueryJobConfiguration.newBuilder(sql).build())
    );

    // TODO this is super fragile
    assertEquals(
        "Raw table has 1 rows missing a primary key at [12:3]",
        e.getError().getMessage()
    );
  }

  @Test
  public void testInsertNewRecordsIncremental() throws InterruptedException {
    createRawTable();
    createFinalTable();
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "raw_table_id", streamId.rawTableId()
        )).replace("""
            INSERT INTO ${raw_table_id} (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES (JSON'{"id": 1, "name": "Alice", "address": {"city": "San Francisco", "state": "CA"}, "updated_at": "2023-01-01T01:00:00Z"}', GENERATE_UUID(), CURRENT_TIMESTAMP());
            INSERT INTO ${raw_table_id} (`_airbyte_data`, `_airbyte_raw_id`, `_airbyte_extracted_at`) VALUES (JSON'{"id": 1, "name": "Alice", "address": {"city": "San Diego", "state": "CA"}, "updated_at": "2023-01-01T02:00:00Z"}', GENERATE_UUID(), CURRENT_TIMESTAMP());
            """)
    ).build());

    final String sql = generator.insertNewRecords(streamId, columns);
    LOGGER.info("Generated sql: {}", sql);
    bq.query(QueryJobConfiguration.newBuilder(sql).build());

    final long finalRows = bq.query(QueryJobConfiguration.newBuilder("SELECT * FROM " + streamId.finalTableId()).build()).getTotalRows();
    assertEquals(2, finalRows);
  }

  private StreamConfig<StandardSQLTypeName> incrementalDedupStreamConfig() {
    return new StreamConfig<>(
        streamId,
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        List.of(generator.quoteColumnId("id")),
        Optional.of(generator.quoteColumnId("updated_at")),
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
    bq.query(QueryJobConfiguration.newBuilder(
        new StringSubstitutor(Map.of(
            "dataset", testDataset
        )).replace("""
            CREATE TABLE ${dataset}.users_final (
              _airbyte_raw_id STRING NOT NULL,
              _airbyte_extracted_at TIMESTAMP NOT NULL,
              _airbyte_meta JSON NOT NULL,
              id INT64,
              updated_at TIMESTAMP,
              name STRING,
              address STRING
            )
            PARTITION BY (DATE_TRUNC(_airbyte_extracted_at, DAY))
            CLUSTER BY id, _airbyte_extracted_at;
            """)
    ).build());
  }
}
