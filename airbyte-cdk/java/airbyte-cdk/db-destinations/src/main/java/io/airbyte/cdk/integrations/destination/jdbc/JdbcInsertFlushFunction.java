/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc;

import io.airbyte.cdk.integrations.destination.async.function.DestinationFlushFunction;
import io.airbyte.cdk.integrations.destination.async.partial_messages.PartialAirbyteMessage;
import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.RecordWriter;
import io.airbyte.cdk.integrations.destination.jdbc.constants.GlobalDataSizeConstants;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.stream.Stream;

public class JdbcInsertFlushFunction implements DestinationFlushFunction {

  private final RecordWriter<PartialAirbyteMessage> recordWriter;

  public JdbcInsertFlushFunction(final RecordWriter<PartialAirbyteMessage> recordWriter) {
    this.recordWriter = recordWriter;
  }

  @Override
  public void flush(final StreamDescriptor desc, final Stream<PartialAirbyteMessage> stream) throws Exception {
    recordWriter.accept(
        new AirbyteStreamNameNamespacePair(desc.getName(), desc.getNamespace()),
        stream.toList());
  }

  @Override
  public long getOptimalBatchSizeBytes() {
    // TODO tune this value - currently SqlOperationUtils partitions 10K records per insert statement,
    // but we'd like to stop doing that and instead control sql insert statement size via batch size.
    return GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES;
  }

}
