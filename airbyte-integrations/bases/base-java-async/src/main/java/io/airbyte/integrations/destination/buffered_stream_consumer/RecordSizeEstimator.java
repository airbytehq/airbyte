/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.buffered_stream_consumer;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.util.HashMap;
import java.util.Map;

/**
 * This class estimate the byte size of the record message. To reduce memory footprint, 1) it
 * assumes that a character is always four bytes, and 2) it only performs a sampling every N
 * records. The size of the samples are averaged together to protect the estimation against
 * outliers.
 */
public class RecordSizeEstimator {

  // by default, perform one estimation for every 20 records
  private static final int DEFAULT_SAMPLE_BATCH_SIZE = 20;

  // latest estimated record message size for each stream
  private final Map<String, Long> streamRecordSizeEstimation;
  // number of record messages until next real sampling for each stream
  private final Map<String, Integer> streamSampleCountdown;
  // number of record messages
  private final int sampleBatchSize;

  /**
   * The estimator will perform a real calculation once per sample batch. The size of the batch is
   * determined by {@code sampleBatchSize}.
   */
  public RecordSizeEstimator(final int sampleBatchSize) {
    this.streamRecordSizeEstimation = new HashMap<>();
    this.streamSampleCountdown = new HashMap<>();
    this.sampleBatchSize = sampleBatchSize;
  }

  public RecordSizeEstimator() {
    this(DEFAULT_SAMPLE_BATCH_SIZE);
  }

  public long getEstimatedByteSize(final AirbyteRecordMessage record) {
    final String stream = record.getStream();
    final Integer countdown = streamSampleCountdown.get(stream);

    // this is a new stream; initialize its estimation
    if (countdown == null) {
      final long byteSize = getStringByteSize(record.getData());
      streamRecordSizeEstimation.put(stream, byteSize);
      streamSampleCountdown.put(stream, sampleBatchSize - 1);
      return byteSize;
    }

    // this stream needs update; compute a new estimation
    if (countdown <= 0) {
      final long prevMeanByteSize = streamRecordSizeEstimation.get(stream);
      final long currentByteSize = getStringByteSize(record.getData());
      final long newMeanByteSize = prevMeanByteSize / 2 + currentByteSize / 2;
      streamRecordSizeEstimation.put(stream, newMeanByteSize);
      streamSampleCountdown.put(stream, sampleBatchSize - 1);
      return newMeanByteSize;
    }

    // this stream does not need update; return current estimation
    streamSampleCountdown.put(stream, countdown - 1);
    return streamRecordSizeEstimation.get(stream);
  }

  @VisibleForTesting
  static long getStringByteSize(final JsonNode data) {
    // assume UTF-8 encoding, and each char is 4 bytes long
    return Jsons.serialize(data).length() * 4L;
  }

}
