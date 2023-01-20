package io.airbyte.integrations.destination.snowflake;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import io.airbyte.commons.json.Jsons;
import io.airbyte.integrations.base.Destination;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.workers.test_utils.AirbyteMessageUtils;
import java.util.List;

public class SnowflakePerformanceTest {

  public static ObjectMapper mapper = new ObjectMapper();
  public static JsonNode config;

  static {
    try {
      config = mapper.readTree(
          "{\"host\": \"\", \"role\": \"\", \"schema\": \"\", \"database\": \"\", \"username\": \"\", \"warehouse\": \"\", \"credentials\": {\"password\": \"\", \"loading_method\": {\"method\": \"Internal Staging\"}}}");
    } catch (JsonProcessingException e) {
      throw new RuntimeException(e);
    }
  }

  public static void main(String[] args) throws Exception {
    final var snowflake = new SnowflakeDestination(OssCloudEnvVarConsts.AIRBYTE_OSS);
    ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog()
        .withStreams(List.of(new ConfiguredAirbyteStream().withSyncMode(SyncMode.FULL_REFRESH).withStream(new AirbyteStream().withName("s1"))
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)));
    final var consumer = snowflake.getConsumer(config, catalog, Destination::defaultOutputRecordCollector);
    AirbyteMessage message = Jsons.convertValue(AirbyteMessageUtils.createRecordMessage("s1", "data",
      "This is a fairly long sentence to provide some bytes here. More bytes is better as it helps us measure performance."
          + "More random string to push the bytes through....."), AirbyteMessage.class);
    var numBytes = message.getRecord().getData().asText().getBytes().length;
    // in a while loop, output to the consumer
    consumer.start();

    var bytesSent = 0;
    var start = System.currentTimeMillis();

    for (int i = 0; i < 5_000_000; i++) {
      consumer.accept(message);
      bytesSent += numBytes;
      if (i % 100000 == 0) {
        System.out.println("sent records: " + i);
      }
    }
    var end = System.currentTimeMillis();
    var timeTakenSecs = (end - start);

    System.out.println(timeTakenSecs);
    consumer.close();
  }

}
