package io.airbyte.integrations.destination.buffered_stream_consumer;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.AirbyteRecordMessage;
import java.util.HashMap;
import java.util.Map;

public class RecordSizeEstimator {

  // by default, perform one estimation for every 20 records
  private static final int DEFAULT_SAMPLE_BATCH_SIZE = 20;

  // latest estimated record message size for each stream
  private final Map<String, Long> streamRecordSizes;
  // number of record messages until next real sampling for each stream
  private final Map<String, Integer> streamSampleCountdown;
  // number of record messages
  private final int sampleBatchSize;

  /**
   * The estimator will perform a real calculation once per sample batch.
   * The size of the batch is determined by {@code sampleBatchSize}.
   */
  public RecordSizeEstimator(final int sampleBatchSize) {
    this.streamRecordSizes = new HashMap<>();
    this.streamSampleCountdown = new HashMap<>();
    this.sampleBatchSize = sampleBatchSize;
  }

  public RecordSizeEstimator() {
    this(DEFAULT_SAMPLE_BATCH_SIZE);
  }

  public long getEstimatedByteSize(final AirbyteRecordMessage recordMessage) {
    final String stream = recordMessage.getStream();
    final Integer countdown = streamSampleCountdown.get(stream);
    if (countdown == null || countdown <= 0) {
      final long byteSize = getStringByteSize(recordMessage.getData());
      streamRecordSizes.put(stream, byteSize);
      streamSampleCountdown.put(stream, sampleBatchSize - 1);
      return byteSize;
    }
    streamSampleCountdown.put(stream, countdown - 1);
    return streamRecordSizes.get(stream);
  }

  @VisibleForTesting
  static long getStringByteSize(final JsonNode data) {
    // assume UTF-8 encoding, and each char is 4 bytes long
    return Jsons.serialize(data).length() * 4L;
  }

}
