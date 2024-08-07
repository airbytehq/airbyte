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
import javax.annotation.CheckForNull;

/**
 * This iterator generates test data to be used in speed benchmarking at airbyte. It is
 * deterministic--if called with the same constructor values twice, it will return the same data.
 * The goal is for it to go fast.
 */
class SpeedBenchmarkGeneratorIterator extends AbstractIterator<AirbyteMessage> {

  private static final String fieldBase = "field";
  private static final String valueBase = "valuevaluevaluevaluevalue";
  private static final AirbyteMessage message = new AirbyteMessage()
      .withType(Type.RECORD)
      .withRecord(new AirbyteRecordMessage().withEmittedAt(Instant.EPOCH.toEpochMilli()).withStream("stream1"));
  private static final JsonNode jsonNode = Jsons.emptyObject();

  private final long maxRecords;
  private long numRecordsEmitted;

  public SpeedBenchmarkGeneratorIterator(final long maxRecords) {
    this.maxRecords = maxRecords;
    numRecordsEmitted = 0;
  }

  @CheckForNull
  @Override
  protected AirbyteMessage computeNext() {
    if (numRecordsEmitted == maxRecords) {
      return endOfData();
    }

    numRecordsEmitted++;

    for (int j = 1; j <= 5; ++j) {
      // do % 10 so that all records are same length.
      ((ObjectNode) jsonNode).put(fieldBase + j, valueBase + numRecordsEmitted % 10);
    }

    message.getRecord().withData(jsonNode);
    return Jsons.clone(message);
  }

}
