package io.airbyte.integrations.destination.buffered_stream_consumer;

import static org.junit.jupiter.api.Assertions.assertEquals;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import org.junit.jupiter.api.Test;

class RecordSizeEstimatorTest {

  private static final JsonNode DATA_0 = Jsons.deserialize("{}");
  private static final JsonNode DATA_1 = Jsons.deserialize("{ \"field1\": true }");
  private static final JsonNode DATA_2 = Jsons.deserialize("{ \"field1\": 10000 }");
  private static final long DATA_0_SIZE = RecordSizeEstimator.getStringByteSize(DATA_0);
  private static final long DATA_1_SIZE = RecordSizeEstimator.getStringByteSize(DATA_1);
  private static final long DATA_2_SIZE = RecordSizeEstimator.getStringByteSize(DATA_2);

  @Test
  public void testPeriodicSampling() {
    // the estimate performs a size sampling every 3 records
    final RecordSizeEstimator sizeEstimator = new RecordSizeEstimator(3);
    final String stream = "stream";
    final AirbyteRecordMessage record0 = new AirbyteRecordMessage().withStream(stream).withData(DATA_0);
    final AirbyteRecordMessage record1 = new AirbyteRecordMessage().withStream(stream).withData(DATA_1);
    final AirbyteRecordMessage record2 = new AirbyteRecordMessage().withStream(stream).withData(DATA_2);

    // sample record message 1
    assertEquals(DATA_1_SIZE, sizeEstimator.getEstimatedByteSize(record1));
    // next two calls return the first sampling result
    assertEquals(DATA_1_SIZE, sizeEstimator.getEstimatedByteSize(record0));
    assertEquals(DATA_1_SIZE, sizeEstimator.getEstimatedByteSize(record0));

    // sample record message 2
    assertEquals(DATA_2_SIZE, sizeEstimator.getEstimatedByteSize(record2));
    // next two calls return the second sampling result
    assertEquals(DATA_2_SIZE, sizeEstimator.getEstimatedByteSize(record0));
    assertEquals(DATA_2_SIZE, sizeEstimator.getEstimatedByteSize(record0));
  }

  @Test
  public void testDifferentEstimationPerStream() {
    final RecordSizeEstimator sizeEstimator = new RecordSizeEstimator();
    final AirbyteRecordMessage record0 = new AirbyteRecordMessage().withStream("stream1").withData(DATA_0);
    final AirbyteRecordMessage record1 = new AirbyteRecordMessage().withStream("stream2").withData(DATA_1);
    final AirbyteRecordMessage record2 = new AirbyteRecordMessage().withStream("stream3").withData(DATA_2);
    assertEquals(DATA_0_SIZE, sizeEstimator.getEstimatedByteSize(record0));
    assertEquals(DATA_1_SIZE, sizeEstimator.getEstimatedByteSize(record1));
    assertEquals(DATA_2_SIZE, sizeEstimator.getEstimatedByteSize(record2));
  }

}
