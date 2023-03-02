/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.google.common.collect.AbstractIterator;
import com.google.common.collect.ImmutableMap;
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

  private static final String FIELD_BASE = "field";
  private static final String VALUE = "valuevaluevaluevaluevalue1";
  private static final AirbyteMessage MESSAGE = new AirbyteMessage()
      .withType(Type.RECORD)
      .withRecord(new AirbyteRecordMessage()
          .withEmittedAt(Instant.EPOCH.toEpochMilli())
          .withStream("stream1")
          .withData(Jsons.jsonNode(ImmutableMap.of(
              FIELD_BASE + "1", VALUE,
              FIELD_BASE + "2", VALUE,
              FIELD_BASE + "3", VALUE,
              FIELD_BASE + "4", VALUE,
              FIELD_BASE + "5", VALUE))));
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
    return MESSAGE;
  }

}
