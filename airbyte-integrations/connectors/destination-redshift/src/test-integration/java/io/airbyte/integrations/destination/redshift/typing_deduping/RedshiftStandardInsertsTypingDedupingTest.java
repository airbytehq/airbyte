/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.redshift.typing_deduping;

import static org.junit.jupiter.api.Assertions.*;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import io.airbyte.commons.io.IOs;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteStream;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream;
import io.airbyte.protocol.models.v0.DestinationSyncMode;
import io.airbyte.protocol.models.v0.SyncMode;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import org.junit.jupiter.api.Test;

public class RedshiftStandardInsertsTypingDedupingTest extends AbstractRedshiftTypingDedupingTest {

  @Override
  protected ObjectNode getBaseConfig() {
    return (ObjectNode) Jsons.deserialize(IOs.readFile(Path.of("secrets/1s1t_config.json")));
  }

  @Test
  public void testStandardInsertBatchSizeGtThan16Mb() throws Exception {
    final String placeholderRecord = """
                                     {"type": "RECORD",
                                       "record":{
                                         "emitted_at": 1000,
                                         "data": {
                                           "id1": 1,
                                           "id2": 200,
                                           "updated_at": "2000-01-01T00:00:00Z",
                                           "_ab_cdc_deleted_at": null,
                                           "name": "PLACE_HOLDER",
                                           "address": {"city": "San Francisco", "state": "CA"}}
                                       }
                                     }
                                     """;
    final ConfiguredAirbyteCatalog catalog = new ConfiguredAirbyteCatalog().withStreams(List.of(
        new ConfiguredAirbyteStream()
            .withSyncMode(SyncMode.FULL_REFRESH)
            .withDestinationSyncMode(DestinationSyncMode.OVERWRITE)
            .withStream(new AirbyteStream()
                .withNamespace(getStreamNamespace())
                .withName(getStreamName())
                .withJsonSchema(getSchema()))));
    List<AirbyteMessage> messages = new ArrayList<>();
    final int numberOfRecords = 1000;
    for (int i = 0; i < numberOfRecords; ++i) {
      // Stuff the record with 40Kb string, making the total record size to 41233 bytes
      // Total sync generates ~39MB in 1000 records.
      // Standard insert should not fail and chunk it into smaller inserts < 16MB statement length
      final AirbyteMessage placeHolderMessage = Jsons.deserialize(placeholderRecord, AirbyteMessage.class);
      placeHolderMessage.getRecord().setNamespace(getStreamNamespace());
      placeHolderMessage.getRecord().setStream(getStreamName());
      ((ObjectNode) placeHolderMessage.getRecord().getData()).put("id1", i);
      ((ObjectNode) placeHolderMessage.getRecord().getData()).put("id2", 200 + i);
      ((ObjectNode) placeHolderMessage.getRecord().getData()).put("name", generateRandomString(40 * 1024));
      messages.add(placeHolderMessage);
    }
    runSync(catalog, messages);
    // we just need to iterate over final tables to verify the count and confirm they are inserted
    // properly.
    List<JsonNode> finalTableResults = dumpFinalTableRecords(getStreamNamespace(), getStreamName());
    assertEquals(1000, finalTableResults.size());
    // getJsons query doesn't have order by clause, so using sum of n-numbers math to assert all IDs are
    // inserted
    int id1sum = 0;
    int id2sum = 0;
    int id1ExpectedSum = ((numberOfRecords - 1) * (numberOfRecords)) / 2; // n(n+1)/2
    int id2ExpectedSum = (200 * numberOfRecords) + id1ExpectedSum; // 200*n + id1Sum
    for (JsonNode record : finalTableResults) {
      id1sum += record.get("id1").asInt();
      id2sum += record.get("id2").asInt();
    }
    assertEquals(id1ExpectedSum, id1sum);
    assertEquals(id2ExpectedSum, id2sum);
  }

}
