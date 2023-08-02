package io.airbyte.integrations.destination.bigquery.typing_deduping;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.DatasetId;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableResult;
import io.airbyte.integrations.base.TypingAndDedupingFlag;
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest;
import io.airbyte.integrations.base.destination.typing_deduping.CatalogParser;
import io.airbyte.integrations.base.destination.typing_deduping.StreamId;
import io.airbyte.integrations.destination.bigquery.BigQueryDestination;
import io.airbyte.integrations.destination.bigquery.BigQueryDestinationTestUtils;
import io.airbyte.integrations.destination.bigquery.BigQueryUtils;
import java.io.IOException;
import java.nio.file.Path;
import java.util.List;

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
  protected List<JsonNode> dumpRawTableRecords(String streamNamespace, String streamName) throws InterruptedException {
    if (streamNamespace == null) {
      streamNamespace = BigQueryUtils.getDatasetId(getConfig());
    }
    TableResult result = bq.query(QueryJobConfiguration.of("SELECT * FROM " + getRawDataset() + "." + StreamId.concatenateRawTableName(streamNamespace, streamName)));
    return BigQuerySqlGeneratorIntegrationTest.toJsonRecords(result);
  }

  @Override
  protected List<JsonNode> dumpFinalTableRecords(String streamNamespace, String streamName) throws InterruptedException {
    if (streamNamespace == null) {
      streamNamespace = BigQueryUtils.getDatasetId(getConfig());
    }
    TableResult result = bq.query(QueryJobConfiguration.of("SELECT * FROM " + streamNamespace + "." + streamName));
    return BigQuerySqlGeneratorIntegrationTest.toJsonRecords(result);
  }

  @Override
  protected void teardownStreamAndNamespace(String streamNamespace, String streamName) {
    if (streamNamespace == null) {
      streamNamespace = BigQueryUtils.getDatasetId(getConfig());
    }
    // bq.delete simply returns false if the table/schema doesn't exist (e.g. if the connector failed to create it)
    // so we don't need to do any existence checks here.
    bq.delete(TableId.of(getRawDataset(), StreamId.concatenateRawTableName(streamNamespace, streamName)));
    bq.delete(DatasetId.of(streamNamespace), BigQuery.DatasetDeleteOption.deleteContents());
  }

  /**
   * Subclasses using a config with a nonstandard raw table dataset should override this method.
   */
  protected String getRawDataset() {
    return CatalogParser.DEFAULT_RAW_TABLE_NAMESPACE;
  }
}
