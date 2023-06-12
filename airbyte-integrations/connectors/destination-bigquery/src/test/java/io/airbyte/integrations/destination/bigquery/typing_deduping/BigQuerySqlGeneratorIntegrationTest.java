package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static io.airbyte.integrations.destination.bigquery.BigQueryDestination.getServiceAccountCredentials;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.auth.oauth2.GoogleCredentials;
import com.google.cloud.bigquery.BigQuery;
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
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.Test;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

// TODO this proooobably belongs in test-integration?
public class BigQuerySqlGeneratorIntegrationTest {

  private static final Logger LOGGER = LoggerFactory.getLogger(BigQuerySqlGeneratorIntegrationTest.class);

  private static final String TEST_DATASET = "bq_sql_generator_test_" + UUID.randomUUID().toString().replace("-", "_");

  private static BigQuery bq;
  private static BigQuerySqlGenerator generator;

  @BeforeAll
  public static void setup() throws Exception {
    LOGGER.info("Running in dataset {}", TEST_DATASET);

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

    bq.create(DatasetInfo.newBuilder(TEST_DATASET).build());
  }

  @AfterAll
  public static void teardown() {
    bq.delete(TEST_DATASET, BigQuery.DatasetDeleteOption.deleteContents());
  }

  @Test
  public void testCreateTable() throws InterruptedException {
    final String sql = generator.createTable(incrementalDedupStreamConfig());

    bq.query(QueryJobConfiguration.newBuilder(sql).build());

    final Table table = bq.getTable(TEST_DATASET, "users");
    assertNotNull(table);
  }

  private StreamConfig<StandardSQLTypeName> incrementalDedupStreamConfig() {
    LinkedHashMap<QuotedColumnId, ParsedType<StandardSQLTypeName>> columns = new LinkedHashMap<>();
    columns.put(generator.quoteColumnId("id"), new ParsedType<>(StandardSQLTypeName.INT64, AirbyteProtocolType.INTEGER));
    columns.put(generator.quoteColumnId("updated_at"), new ParsedType<>(StandardSQLTypeName.TIMESTAMP, AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE));
    columns.put(generator.quoteColumnId("name"), new ParsedType<>(StandardSQLTypeName.STRING, AirbyteProtocolType.STRING));

    LinkedHashMap<String, AirbyteType> addressProperties = new LinkedHashMap<>();
    addressProperties.put("city", AirbyteProtocolType.STRING);
    addressProperties.put("state", AirbyteProtocolType.STRING);
    columns.put(generator.quoteColumnId("address"), new ParsedType<>(StandardSQLTypeName.STRING, new Struct(addressProperties)));

    return new StreamConfig<>(
        new SqlGenerator.QuotedStreamId(TEST_DATASET, "users", TEST_DATASET, "public_users", "public", "users"),
        SyncMode.INCREMENTAL,
        DestinationSyncMode.APPEND_DEDUP,
        List.of(generator.quoteColumnId("id")),
        Optional.of(generator.quoteColumnId("updated_at")),
        columns
    );
  }
}
