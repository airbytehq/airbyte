package io.airbyte.integrations.source.postgres;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class PostgresPerformanceTest {

  public static ObjectMapper mapper = new ObjectMapper();
  public static JsonNode config;

  static {
    try {
      config = mapper.readTree(
          "{\"host\": \"davin-performance-test.cuczxc1ksccg.us-east-2.rds.amazonaws.com\", \"port\": 5432, \"schemas\": [\"public\"], \"database\": \"postgres\", \"password\": \"\", \"ssl_mode\": {\"mode\": \"require\"}, \"username\": \"\", \"tunnel_method\": {\"tunnel_method\": \"NO_TUNNEL\"}, \"replication_method\": {\"method\": \"Standard\"}}");
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }
  }

  // This tests the Postgres Source itself. This does not include the integration runner. 
  // Does including the integration runner change things?
  public static void main(String[] args) {
    directlyTestPostgresSource();
  }

  private static void directlyTestPostgresSource() {
    try (PostgresSource postgres = new PostgresSource()) {
      var catalog = Jsons.deserialize(
          "{\"streams\":[{\"stream\":{\"name\":\"towns\",\"namespace\":\"public\",\"json_schema\":{\"type\":\"object\",\"properties\":{\"id\":{\"type\":\"number\",\"airbyte_type\":\"integer\"},\"code\":{\"type\":\"string\"},\"name\":{\"type\":\"string\"},\"article\":{\"type\":\"string\"}}},\"default_cursor_field\":[],\"supported_sync_modes\":[\"full_refresh\",\"incremental\"],\"source_defined_primary_key\":[]},\"sync_mode\":\"full_refresh\",\"primary_key\":[],\"cursor_field\":[],\"destination_sync_mode\":\"overwrite\"}]}",
          ConfiguredAirbyteCatalog.class);
      var state = mapper.createObjectNode();

      final var iterator = postgres.read(config, catalog, state);

      var totalMB = 0.0;
      var counter = 0;
      var start = System.currentTimeMillis();
      while (iterator.hasNext()) {
        var record = iterator.next();
        totalMB += (record.getRecord().getData().toString().getBytes().length / 1_000_000.0);
        counter++;

        if (counter % 3_000_000 == 0) {
          break;
        }
      }
      var end = System.currentTimeMillis();
      var totalTimeSecs = (end - start) / 1000.0;

      log.info("total secs: {}. total MB read: {}, throughput: {}", totalTimeSecs, totalMB, totalMB / totalTimeSecs);
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

}
