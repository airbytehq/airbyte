/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.DatasetId;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableResult;
import io.airbyte.cdk.integrations.base.JavaBaseConstants;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest;
import io.airbyte.integrations.base.destination.typing_deduping.SqlGenerator;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.bigquery.BigQueryConsts;
import io.airbyte.integrations.destination.bigquery.BigQueryDestination;
import io.airbyte.integrations.destination.bigquery.BigQueryDestinationTestUtils;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import io.airbyte.workers.exception.TestHarnessException;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import org.junit.jupiter.api.Test;

public abstract class AbstractBigQueryTypingDedupingTest extends BaseTypingDedupingTest {

  private BigQuery bq;

  protected abstract String getConfigPath();

  @Override
  public JsonNode generateConfig() throws IOException {
    final String datasetId = "typing_deduping_default_dataset" + getUniqueSuffix();
    final String stagingPath = "test_path" + getUniqueSuffix();
    final ObjectNode config = BigQueryDestinationTestUtils.createConfig(Path.of(getConfigPath()), datasetId, stagingPath);
    bq = BigQueryDestination.getBigQuery(config);
    return config;
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-bigquery:dev";
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(String streamNamespace, final String streamName) throws InterruptedException {
    if (streamNamespace == null) {
      streamNamespace = BigQueryUtils.getDatasetId(getConfig());
    }
    final TableResult result =
        bq.query(QueryJobConfiguration.of("SELECT * FROM " + getRawDataset() + "." + StreamId.concatenateRawTableName(streamNamespace, streamName)));
    return BigQuerySqlGeneratorIntegrationTest.toJsonRecords(result);
  }

  @Override
  public List<JsonNode> dumpFinalTableRecords(String streamNamespace, final String streamName) throws InterruptedException {
    if (streamNamespace == null) {
      streamNamespace = BigQueryUtils.getDatasetId(getConfig());
    }
    final TableResult result = bq.query(QueryJobConfiguration.of("SELECT * FROM " + streamNamespace + "." + streamName));
    return BigQuerySqlGeneratorIntegrationTest.toJsonRecords(result);
  }

  @Override
  protected void teardownStreamAndNamespace(String streamNamespace, final String streamName) {
    if (streamNamespace == null) {
      streamNamespace = BigQueryUtils.getDatasetId(getConfig());
    }
    // bq.delete simply returns false if the table/schema doesn't exist (e.g. if the connector failed to
    // create it)
    // so we don't need to do any existence checks here.
    bq.delete(TableId.of(getRawDataset(), StreamId.concatenateRawTableName(streamNamespace, streamName)));
    bq.delete(DatasetId.of(streamNamespace), BigQuery.DatasetDeleteOption.deleteContents());
  }

  @Override
  protected SqlGenerator getSqlGenerator() {
    return new BigQuerySqlGenerator(getConfig().get(BigQueryConsts.CONFIG_PROJECT_ID).asText(), null);
  }

  @Test
  public void testV1V2Migration() throws Exception {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.APPEND)
            .withStream(new AirbyteStream()
                .withNamespace(getStreamNamespace())
                .withName(getStreamName())
                .withJsonSchema(SCHEMA))));

    // First sync
    final List<AirbyteMessage> messages1 = readMessages("dat/sync1_messages.jsonl");

    runSync(catalog, messages1, "airbyte/destination-bigquery:1.10.2", config -> {
      // Defensive to avoid weird behaviors or test failures if the original config is being altered by
      // another thread, thanks jackson for a mutable JsonNode
      JsonNode copiedConfig = Jsons.clone(config);
      if (config instanceof ObjectNode) {
        // Opt out of T+D to run old V1 sync
        ((ObjectNode) copiedConfig).put("use_1s1t_format", false);
      }
      return copiedConfig;
    });

    // The record differ code is already adapted to V2 columns format, use the post V2 sync
    // to verify that append mode preserved all the raw records and final records.

    // Second sync
    final List<AirbyteMessage> messages2 = readMessages("dat/sync2_messages.jsonl");

    runSync(catalog, messages2);

    final List<JsonNode> expectedRawRecords2 = readRecords("dat/sync2_expectedrecords_raw.jsonl");
    final List<JsonNode> expectedFinalRecords2 = readRecords("dat/sync2_expectedrecords_fullrefresh_append_final.jsonl");
    verifySyncResult(expectedRawRecords2, expectedFinalRecords2, disableFinalTableComparison());
  }

  @Test
  public void testRemovingPKNonNullIndexes() throws Exception {
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.INCREMENTAL)
            .withDestinationSyncMode(DestinationSyncMode.APPEND_DEDUP)
            .withPrimaryKey(List.of(List.of("id1"), List.of("id2")))
            .withStream(new AirbyteStream()
                .withNamespace(getStreamNamespace())
                .withName(getStreamName())
                .withJsonSchema(SCHEMA))));

    // First sync
    final List<AirbyteMessage> messages = readMessages("dat/sync_null_pk.jsonl");
    final TestHarnessException e = assertThrows(
        TestHarnessException.class,
        () -> runSync(catalog, messages, "airbyte/destination-bigquery:2.0.20")); // this version introduced non-null PKs to the final tables
    // ideally we would assert on the logged content of the original exception within e, but that is
    // proving to be tricky

    // Second sync
    runSync(catalog, messages); // does not throw with latest version
    assertEquals(1, dumpFinalTableRecords(getStreamNamespace(), getStreamName()).toArray().length);
  }

  /**
   * Subclasses using a config with a nonstandard raw table dataset should override this method.
   */
  protected String getRawDataset() {
    return JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE;
  }

}
