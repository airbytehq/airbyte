package io.airbyte.cdk.integrations.destination.jdbc;

import io.airbyte.cdk.integrations.destination.buffered_stream_consumer.RecordWriter;
import io.airbyte.cdk.integrations.destination_async.DestinationFlushFunction;
import io.airbyte.cdk.integrations.destination_async.partial_messages.PartialAirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteRecordMessage;
import io.airbyte.protocol.models.v0.AirbyteStreamNameNamespacePair;
import io.airbyte.protocol.models.v0.StreamDescriptor;
import java.util.stream.Stream;

public class JdbcInsertFlushFunction implements DestinationFlushFunction {

  private final RecordWriter<AirbyteRecordMessage> recordWriter;

  public JdbcInsertFlushFunction(final RecordWriter<AirbyteRecordMessage> recordWriter) {
    this.recordWriter = recordWriter;
  }

  @Override
  public void flush(final StreamDescriptor desc, final Stream<PartialAirbyteMessage> stream) throws Exception {
    // TODO we can probably implement this better - use the serialized data string directly instead of redeserializing it for insertRecords
    recordWriter.accept(
        new AirbyteStreamNameNamespacePair(desc.getName(), desc.getNamespace()),
        stream.map(PartialAirbyteMessage::getFullRecordMessage).toList()
    );
  }

  @Override
  public long getOptimalBatchSizeBytes() {
    // SQL statements probably shouldn't be very large
    // so limit ourselves to 5MB of data per insert statement
    return 5 * 1024 * 1024;
  }
}
