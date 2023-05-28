/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import java.time.Instant;
import java.util.Random;
import javax.annotation.CheckForNull;

/**
 * This iterator generates test data to be used in speed benchmarking at airbyte. It is
 * deterministic--if called with the same constructor values twice, it will return the same data.
 * The goal is for it to go fast.
 */
class SpeedBenchmark5ColumnGeneratorIterator extends AbstractIterator<AirbyteMessage> {

  private static final long FIXED_TIME = Instant.EPOCH.toEpochMilli();
  private static final String STREAM_BASE = "stream";
  private static final int FIRST_COLUMN_SUFFIX = 1;
  private static final int COLUMN_COUNT = 5;
  private static final String COLUMN_BASE = "field";
  private static final String VALUE_BASE = "valuevaluevaluevaluevalue";

  private final String valueBaseWithThread;

  private final long maxRecords;
  private long numRecordsEmitted;
  private final int streamCount;
  private final Random random;

  private final String[] columnNames;

  public SpeedBenchmark5ColumnGeneratorIterator(final long maxRecords, final int streamCount, final int threadNum) {
    this.maxRecords = maxRecords;
    this.streamCount = streamCount;
    numRecordsEmitted = 0;
    random = new Random(54321);
    columnNames = generateFields();
    valueBaseWithThread = VALUE_BASE + "-" + threadNum + "-";
  }

  private static String[] generateFields() {
    final String[] columnNames = new String[5];
    for (int i = FIRST_COLUMN_SUFFIX; i <= COLUMN_COUNT; i++) {
      columnNames[i - 1] = COLUMN_BASE + i;
    }
    return columnNames;
  }

  @CheckForNull
  @Override
  protected AirbyteMessage computeNext() {
    if (numRecordsEmitted == maxRecords) {
      return endOfData();
    }

    numRecordsEmitted++;

    final JsonNode jsonNode = Jsons.emptyObject();
    for (int j = FIRST_COLUMN_SUFFIX; j <= COLUMN_COUNT; ++j) {
      // do % 10 so that all records are same length.
      ((ObjectNode) jsonNode).put(columnNames[j - 1], valueBaseWithThread + numRecordsEmitted % 10);
    }

    return new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage()
            .withEmittedAt(FIXED_TIME)
            .withStream(streamCount == 1 ? STREAM_BASE + "1" : STREAM_BASE + (random.nextInt(streamCount) + 1))
            .withData(jsonNode));
  }

}
