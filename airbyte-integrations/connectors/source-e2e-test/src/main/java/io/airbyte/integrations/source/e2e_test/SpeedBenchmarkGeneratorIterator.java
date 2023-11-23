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
import io.airbyte.protocol.protos.AirbyteStreamState;
import io.airbyte.protocol.protos.StreamDescriptor;
import java.time.Instant;
import javax.annotation.CheckForNull;

/**
 * This iterator generates test data to be used in speed benchmarking at airbyte. It is
 * deterministic--if called with the same constructor values twice, it will return the same data.
 * The goal is for it to go fast.
 */
class SpeedBenchmarkGeneratorIterator extends AbstractIterator<AirbyteMessage> {

  private static final String STR_BASE = "str";
  private static final String SHORT_INT_BASE = "sint";
  private static final String LONG_INT_BASE = "lint";
  private static final String SHORT_FLOAT_BASE = "sfl";
  private static final String LONG_FLOAT_BASE = "lfl";
  private static final String VALUE_BASE = "valuevaluevaluevaluevalue";
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
//      ((ObjectNode) jsonNode).put(STR_BASE + j, VALUE_BASE + numRecordsEmitted % 10);
      ((ObjectNode) jsonNode).put(SHORT_INT_BASE + j, 1);
      ((ObjectNode) jsonNode).put(LONG_INT_BASE + j, Integer.MAX_VALUE);
      ((ObjectNode) jsonNode).put(SHORT_FLOAT_BASE + j, 1.0);
      ((ObjectNode) jsonNode).put(LONG_FLOAT_BASE + j, 9999999.999999999999999);
    }

    message.getRecord().withData(jsonNode);
    return Jsons.clone(message);
  }

  public static void main(String[] args) {
    System.out.println("poop");

    System.out.println(AirbyteStreamState.getDefaultInstance().isInitialized());
    System.out.println(AirbyteStreamState.newBuilder().setStreamDescriptor(StreamDescriptor.newBuilder().setName("Test").build()));
  }

}
