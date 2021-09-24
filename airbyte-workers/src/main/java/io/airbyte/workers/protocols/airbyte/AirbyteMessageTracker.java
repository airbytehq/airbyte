/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols.airbyte;

import com.google.common.base.Charsets;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.State;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.workers.protocols.MessageTracker;
import java.util.Optional;
import java.util.concurrent.atomic.AtomicLong;
import java.util.concurrent.atomic.AtomicReference;

public class AirbyteMessageTracker implements MessageTracker<AirbyteMessage> {

  private final AtomicLong recordCount;
  private final AtomicLong numBytes;
  private final AtomicReference<State> outputState;

  public AirbyteMessageTracker() {
    this.recordCount = new AtomicLong();
    this.numBytes = new AtomicLong();
    this.outputState = new AtomicReference<>();
  }

  @Override
  public void accept(AirbyteMessage message) {
    if (message.getType() == AirbyteMessage.Type.RECORD) {
      recordCount.incrementAndGet();
      // todo (cgardens) - pretty wasteful to do an extra serialization just to get size.
      numBytes.addAndGet(Jsons.serialize(message.getRecord().getData()).getBytes(Charsets.UTF_8).length);
    }
    if (message.getType() == AirbyteMessage.Type.STATE) {
      outputState.set(new State().withState(message.getState().getData()));
    }
  }

  @Override
  public long getRecordCount() {
    return recordCount.get();
  }

  @Override
  public long getBytesCount() {
    return numBytes.get();
  }

  @Override
  public Optional<State> getOutputState() {
    return Optional.ofNullable(outputState.get());
  }

}
