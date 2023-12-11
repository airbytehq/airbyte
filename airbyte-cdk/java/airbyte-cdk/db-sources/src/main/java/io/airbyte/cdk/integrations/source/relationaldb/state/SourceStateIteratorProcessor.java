package io.airbyte.cdk.integrations.source.relationaldb.state;

import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteStateMessage;
import java.time.Instant;

public interface SourceStateIteratorProcessor {
  AirbyteStateMessage generateStateMessageAtCheckpoint();

  void processRecordMessage(final AirbyteMessage message);
  AirbyteStateMessage createFinalStateMessage();

  boolean shouldEmitStateMessage(final long recordCount, final Instant lastCheckpoint);
}
