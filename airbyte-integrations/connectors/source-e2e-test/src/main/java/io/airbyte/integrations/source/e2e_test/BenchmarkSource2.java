/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.e2e_test;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.google.common.collect.AbstractIterator;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.integrations.BaseConnector;
import io.airbyte.integrations.base.Source;
import io.airbyte.protocol.models.v0.AirbyteCatalog;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus;
import io.airbyte.protocol.models.v0.AirbyteConnectionStatus.Status;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog;
import java.time.Instant;
import javax.annotation.CheckForNull;

/**
 * This source is optimized for creating records very fast. It optimizes for speed over flexibility.
 */
public class BenchmarkSource2 extends BaseConnector implements Source {

  @Override
  public AirbyteConnectionStatus check(final JsonNode jsonConfig) {
    try {
      final BenchmarkConfig sourceConfig = BenchmarkConfig.parseFromConfig(jsonConfig);
      return new AirbyteConnectionStatus().withStatus(Status.SUCCEEDED).withMessage("Source config: " + sourceConfig);
    } catch (final Exception e) {
      return new AirbyteConnectionStatus().withStatus(Status.FAILED).withMessage(e.getMessage());
    }
  }

  @Override
  public AirbyteCatalog discover(final JsonNode jsonConfig) throws Exception {
    final BenchmarkConfig sourceConfig = BenchmarkConfig.parseFromConfig(jsonConfig);
    return sourceConfig.getCatalog();
  }

  static class NumRecordsIterator extends AbstractIterator<AirbyteMessage> {
    private static final String fieldBase = "field";
    private static final String valueBase = "valuevaluevaluevaluevalue";
    private static final AirbyteMessage message = new AirbyteMessage()
        .withType(Type.RECORD)
        .withRecord(new AirbyteRecordMessage().withEmittedAt(Instant.EPOCH.toEpochMilli()).withStream("stream1"));
    private static final JsonNode jsonNode = Jsons.emptyObject();

    private final long maxRecords;
    private long numRecordsEmitted;

    public NumRecordsIterator(final long maxRecords) {
      this.maxRecords = maxRecords;
      numRecordsEmitted = 0;
    }

    @CheckForNull
    @Override
    protected AirbyteMessage computeNext() {
      if(numRecordsEmitted == maxRecords) {
        return endOfData();
      }

      numRecordsEmitted++;

      for (int j = 1; j <= 5; ++j) {
        // do % 10 so that all records are same length.
        ((ObjectNode)jsonNode).put(fieldBase + j, valueBase + numRecordsEmitted % 10);
      }

      message.getRecord().withData(jsonNode);
      return Jsons.clone(message);
    }
  }

  @Override
  public AutoCloseableIterator<AirbyteMessage> read(final JsonNode jsonConfig, final ConfiguredAirbyteCatalog catalog, final JsonNode state)
      throws Exception {
    final BenchmarkConfig sourceConfig = BenchmarkConfig.parseFromConfig(jsonConfig);
    return AutoCloseableIterators.fromIterator(new NumRecordsIterator(sourceConfig.maxRecords()));
  }

}
