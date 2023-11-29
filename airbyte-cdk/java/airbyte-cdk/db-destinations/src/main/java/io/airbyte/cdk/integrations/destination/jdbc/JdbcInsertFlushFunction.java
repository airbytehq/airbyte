/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.jdbc;

import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.RecordWriter;
import io.airbyte.cdk.integrations.destination.jdbc.constants.GlobalDataSizeConstants;
import io.airbyte.cdk.integrations.destination_async.DestinationFlushFunction;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
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
    // use 2MB batches.
    // historical context:
    // old JDBC connectors actually split their batches down into 10K record partitions,
    // so they use GlobalDataSizeConstants.DEFAULT_MAX_BATCH_SIZE_BYTES batches (i.e. 25MiB).
    // we want to stop doing that partitioning and just rely on these batches to be right-sized,
    // so shrinking down the batches. 2MB is a conservative estimate; we'll need to tune it.
    // destination-redshift is the first destination to use this behavior, which will be done
    // as part of the DV2 work.
    return 2 * 1024 * 1024;
  }

}
