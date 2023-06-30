package io.airbyte.integrations.destination.bigquery.typing_deduping;

import static java.util.stream.Collectors.joining;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.DatasetId;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.bigquery.TableResult;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.string.Strings;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType;
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType.Struct;
import io.airbyte.integrations.base.destination.typing_deduping.BaseTypingDedupingTest;
import io.airbyte.integrations.destination.bigquery.BigQueryDestination;
import io.airbyte.integrations.destination.bigquery.BigQueryDestinationTestUtils;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.io.IOException;
import java.nio.file.Path;
import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.apache.commons.text.StringSubstitutor;
import org.junit.jupiter.api.BeforeAll;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class BigQueryStandardInsertsTypingDedupingTest extends BaseTypingDedupingTest {
  private static final Logger LOGGER = LoggerFactory.getLogger(BigQueryStandardInsertsTypingDedupingTest.class);

  private static BigQuery bq;

  // Note that this is not an @Override, because it's a static method. I would love suggestions on how to do this better :)
  @BeforeAll
  public static void buildConfig() throws IOException {
    final String datasetId = Strings.addRandomSuffix("typing_deduping_default_dataset", "_", 5);
    LOGGER.info("Setting default dataset to {}", datasetId);
    config = BigQueryDestinationTestUtils.createConfig(Path.of("secrets/credentials-1s1t-standard.json"), datasetId);
    bq = BigQueryDestination.getBigQuery(config);
  }

  @Override
  protected String getImageName() {
    return "airbyte/destination-bigquery:dev";
  }

  @Override
  protected List<JsonNode> dumpRawTableRecords(String streamNamespace, String streamName) throws InterruptedException {
    TableResult result = bq.query(QueryJobConfiguration.of("SELECT * FROM airbyte." + streamNamespace + "_" + streamName));
    List<LinkedHashMap<String, Object>> rowsAsMaps = BigQuerySqlGeneratorIntegrationTest.toMaps(result);
    return rowsAsMaps.stream().map(BigQueryStandardInsertsTypingDedupingTest::toJson).toList();
  }

  @Override
  protected List<JsonNode> dumpFinalTableRecords(String streamNamespace, String streamName) throws InterruptedException {
    TableResult result = bq.query(QueryJobConfiguration.of("SELECT * FROM " + streamNamespace + "." + streamName));
    List<LinkedHashMap<String, Object>> rowsAsMaps = BigQuerySqlGeneratorIntegrationTest.toMaps(result);
    return rowsAsMaps.stream().map(BigQueryStandardInsertsTypingDedupingTest::toJson).toList();
  }

  @Override
  protected void teardownStreamAndNamespace(String streamNamespace, String streamName) {
    bq.delete(TableId.of("airbyte", streamNamespace + "_" + streamName));
    bq.delete(DatasetId.of(streamNamespace), BigQuery.DatasetDeleteOption.deleteContents());
  }

  private static JsonNode toJson(LinkedHashMap<String, Object> map) {
    ObjectNode o = (ObjectNode) Jsons.emptyObject();
    for (Map.Entry<String, Object> entry : map.entrySet()) {
      Object value = entry.getValue();
      if (value instanceof Instant i) {
        // naively serializing an Instant returns a DecimalNode with the unix epoch, so manually dump the string here.
        o.set(entry.getKey(), Jsons.jsonNode(i.toString()));
      } else {
        o.set(entry.getKey(), Jsons.jsonNode(value));
      }
    }
    return o;
  }
}
