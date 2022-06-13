/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ResetSourceConfiguration;
import io.airbyte.config.StreamDescriptor;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStreamState;
import java.nio.file.Path;
import java.util.Optional;
import java.util.Stack;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * This source will never emit any messages. It can be used in cases where that is helpful (hint:
 * reset connection jobs).
 */
public class EmptyAirbyteSource implements AirbyteSource {

  private final AtomicBoolean hasEmittedState;
  private final Stack<StreamDescriptor> streamDescriptors = new Stack<>();
  private boolean isPartialReset;

  public EmptyAirbyteSource() {
    hasEmittedState = new AtomicBoolean();
  }

  @Override
  public void start(final WorkerSourceConfig sourceConfig, final Path jobRoot) throws Exception {
    try {
      ResetSourceConfiguration sourceConfiguration = Jsons.object(sourceConfig.getSourceConnectionConfiguration(), ResetSourceConfiguration.class);
      streamDescriptors.addAll(sourceConfiguration.getStreamsToReset());
      if (streamDescriptors.isEmpty()) {
        isPartialReset = false;
      } else {
        isPartialReset = true;
      }
    } catch (IllegalArgumentException e) {
      // No op, the new format is not supported
      isPartialReset = false;
    }
  }

  // always finished. it has no data to send.
  @Override
  public boolean isFinished() {
    return hasEmittedState.get();
  }

  @Override
  public int getExitValue() {
    return 0;
  }

  @Override
  public Optional<AirbyteMessage> attemptRead() {
    if (isPartialReset) {
      if (!streamDescriptors.isEmpty()) {
        StreamDescriptor streamDescriptor = streamDescriptors.pop();
        AirbyteMessage responseMessage = new AirbyteMessage()
            .withState(
                new AirbyteStateMessage()
                    .withStream(new AirbyteStreamState()
                        .withStreamDescriptor(
                            new io.airbyte.protocol.models.StreamDescriptor()
                                .withName(streamDescriptor.getName())
                                .withNamespace(streamDescriptor.getNamespace()))
                        .withStreamState(null)));
        return Optional.of(responseMessage);
      } else {
        return Optional.empty();
      }
    } else {
      if (!hasEmittedState.get()) {
        hasEmittedState.compareAndSet(false, true);
        return Optional.of(new AirbyteMessage().withType(Type.STATE).withState(new AirbyteStateMessage().withData(Jsons.emptyObject())));
      } else {
        return Optional.empty();
      }
    }
  }

  @Override
  public void close() throws Exception {
    // no op.
  }

  @Override
  public void cancel() throws Exception {
    // no op.
  }

}
