/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.AbstractIterator;
import datadog.trace.api.Trace;
import io.airbyte.commons.json.Jsons;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.opentracing.Scope;
import io.opentracing.Span;
import io.opentracing.util.GlobalTracer;

import java.time.Instant;
import java.util.Queue;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;
import javax.annotation.CheckForNull;

/**
 * This iterator generates test data to be used in speed benchmarking at airbyte. It is
 * deterministic--if called with the same constructor values twice, it will return the same data.
 * The goal is for it to go fast.
 */
class SpeedBenchmarkGeneratorIterator extends AbstractIterator<AirbyteMessage> {

  private static final String fieldBase = "field";
  private static final String valueBase = "valuevaluevaluevaluevalue";
  private static final Long TIMEOUT_MS = TimeUnit.MINUTES.toMillis(1);

  private final long maxRecords;
  private final AtomicLong numRecordsEmitted;
  private final Executor executor = Executors.newSingleThreadExecutor();
  private final BlockingQueue<AirbyteMessage> buffer;

  public SpeedBenchmarkGeneratorIterator(final long maxRecords) {
    this.maxRecords = maxRecords;
    numRecordsEmitted = new AtomicLong(0);
    final int bufferCapacity = Long.valueOf(Math.round(maxRecords*.20)).intValue();
    buffer = new LinkedBlockingQueue<>(Math.max(bufferCapacity, 1000));
    executor.execute(this::generateData);
  }

  @CheckForNull
  @Override
  @SuppressWarnings("try")
  protected AirbyteMessage computeNext() {
    final Span span = GlobalTracer.get().buildSpan("computeNext").asChildOf(GlobalTracer.get().activeSpan()).start();
    try (final Scope ignored = GlobalTracer.get().activateSpan(span)) {
      if (numRecordsEmitted.get() == maxRecords) {
        return endOfData();
      }

      try {
        // Wait up to the timeout for data to be available.  If not, consider the generation side complete and end the stream
        final AirbyteMessage message = buffer.poll(TIMEOUT_MS, TimeUnit.MILLISECONDS);
        if (message != null) {
          return Jsons.clone(message);
        } else {
          return endOfData();
        }
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
  }

  private void generateData() {
    while(numRecordsEmitted.get() < maxRecords) {
      try {
        final AirbyteMessage message = new AirbyteMessage()
                .withType(Type.RECORD)
                .withRecord(new AirbyteRecordMessage().withEmittedAt(Instant.EPOCH.toEpochMilli()).withStream("stream1"));
        final JsonNode jsonNode = Jsons.emptyObject();
        for (int j = 1; j <= 5; ++j) {
          // do % 10 so that all records are same length.
          ((ObjectNode) jsonNode).put(fieldBase + j, valueBase + numRecordsEmitted.get() % 10);
        }

        message.getRecord().withData(jsonNode);
        buffer.put(message);
        numRecordsEmitted.incrementAndGet();
      } catch (InterruptedException e) {
        throw new RuntimeException(e);
      }
    }
  }
}
