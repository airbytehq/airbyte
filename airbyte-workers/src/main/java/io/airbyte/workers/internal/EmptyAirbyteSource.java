/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ResetSourceConfiguration;
import io.airbyte.config.StreamDescriptor;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.protocol.models.AirbyteGlobalState;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.StateMessageHelper;
import io.vavr.control.Either;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.EmptyStackException;
import java.util.LinkedList;
import java.util.List;
import java.util.Optional;
import java.util.Queue;
import java.util.Stack;
import java.util.concurrent.atomic.AtomicBoolean;
import lombok.extern.slf4j.Slf4j;

/**
 * This source will never emit any messages. It can be used in cases where that is helpful (hint:
 * reset connection jobs).
 */
@Slf4j
public class EmptyAirbyteSource implements AirbyteSource {

  private final AtomicBoolean hasEmittedState;
  private final Queue<StreamDescriptor> streamDescriptors = new LinkedList<>();
  private boolean isPartialReset;
  private boolean isStarted = false;
  private Either<List<AirbyteStateMessage>, AirbyteStateMessage> perStreamOrGlobalState;

  public EmptyAirbyteSource() {
    hasEmittedState = new AtomicBoolean();
  }

  @Override
  public void start(final WorkerSourceConfig sourceConfig, final Path jobRoot) throws Exception {

    try {
      if (sourceConfig == null || sourceConfig.getSourceConnectionConfiguration() == null) {
        isPartialReset = false;
      } else {
        ResetSourceConfiguration sourceConfiguration = Jsons.object(sourceConfig.getSourceConnectionConfiguration(), ResetSourceConfiguration.class);
        streamDescriptors.addAll(sourceConfiguration.getStreamsToReset());
        if (streamDescriptors.isEmpty()) {
          isPartialReset = false;
        } else {
          Either<JsonNode, List<AirbyteStateMessage>> eitherState = StateMessageHelper.getTypedState(sourceConfig.getState().getState());
          if (eitherState.isLeft()) {
            log.error("The state is not compatible with a partial reset that  have been requested");
            throw new IllegalStateException("Legacy state for a partial reset");
          }

          if (eitherState.isRight()) {
            List<AirbyteStateMessage> stateMessages = eitherState.get();
            List<AirbyteStateMessage> stateMessagesPerStreamOnly =
                stateMessages.stream().filter(stateMessage -> stateMessage.getStateType() == AirbyteStateType.STREAM).toList();
            if (stateMessages.isEmpty()) {
              log.error("No state has been provide, no reset will be perform, this will wun nothing");
              streamDescriptors.clear();
            } else if (stateMessages.size() == 1 && stateMessages.get(0).getStateType() == AirbyteStateType.GLOBAL) {
              // Global
              perStreamOrGlobalState = Either.right(stateMessages.get(0));
            } else if (stateMessagesPerStreamOnly.size() == stateMessages.size()) {
              // Per Stream
              perStreamOrGlobalState = Either.left(stateMessages);
            } else {
              throw new IllegalStateException("The state that the empty source recieved is in an unexpected format and can not be use");
            }
          }
          isPartialReset = true;
        }
      }
    } catch (IllegalArgumentException e) {
      // No op, the new format is not supported
      isPartialReset = false;
    }
    isStarted = true;
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
    if (!isStarted) {
      throw new IllegalStateException("The empty source has not been started.");
    }

    if (isPartialReset) {
      if (perStreamOrGlobalState.isLeft()) {
        // Per stream, it will emit one message per stream being reset
        if (!streamDescriptors.isEmpty()) {
          StreamDescriptor streamDescriptor = streamDescriptors.poll();
          List<AirbyteStateMessage> stateMessages = perStreamOrGlobalState.getLeft();
          try {
            while (hasState(stateMessages, streamDescriptor)) {
              streamDescriptor = streamDescriptors.poll();
            }
            return Optional.of(getNullPerStreamMessage(streamDescriptor));
          } catch (EmptyStackException e) {
            return Optional.empty();
          }
        } else {
          return Optional.empty();
        }
      } else {
        // global state, it will emit one global message
        if (hasEmittedState.get()) {
          return Optional.empty();
        } else {
          hasEmittedState.compareAndSet(false, true);
          return Optional.of(getNullGlobalMessage(streamDescriptors, perStreamOrGlobalState.get()));
        }
      }
    } else {
      if (!hasEmittedState.get()) {
        hasEmittedState.compareAndSet(false, true);
        return Optional.of(new AirbyteMessage().withType(Type.STATE)
            .withState(new AirbyteStateMessage().withStateType(AirbyteStateType.LEGACY).withData(Jsons.emptyObject())));
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

  private boolean hasState(List<AirbyteStateMessage> stateMessages, StreamDescriptor streamDescriptor) {
    return stateMessages.stream().filter(stateMessage -> stateMessage.getStream().getStreamDescriptor().equals(streamDescriptor)).count() != 0;
  }

  private AirbyteMessage getNullPerStreamMessage(StreamDescriptor configStreamDescriptor) {
    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(
            new AirbyteStateMessage()
                .withStateType(AirbyteStateType.STREAM)
                .withStream(
                    new AirbyteStreamState()
                        .withStreamDescriptor(new io.airbyte.protocol.models.StreamDescriptor()
                            .withName(configStreamDescriptor.getName())
                            .withNamespace(configStreamDescriptor.getNamespace()))
                        .withStreamState(null)));
  }

  private AirbyteMessage getNullGlobalMessage(Queue<StreamDescriptor> configStreamDescriptors, AirbyteStateMessage currentState) {
    AirbyteGlobalState globalState = new AirbyteGlobalState();
    globalState.setStreamStates(new ArrayList<>());

    currentState.getGlobal().getStreamStates().forEach(exitingState -> globalState.getStreamStates()
            .add(
              new AirbyteStreamState()
                  .withStreamDescriptor(exitingState.getStreamDescriptor())
                  .withStreamState(
                      configStreamDescriptors.contains(new StreamDescriptor()
                          .withName(exitingState.getStreamDescriptor().getName())
                          .withNamespace(exitingState.getStreamDescriptor().getNamespace())) ?
                            null : exitingState.getStreamState()
                  )
            )
    );

    if (currentState.getGlobal().getStreamStates().size() ==
        globalState.getStreamStates().stream().filter(streamState -> streamState.getStreamState() == null).count()) {
      log.info("All the streams of a global state have been reset, the shared state will be erased as well");
      globalState.setSharedState(null);
    } else {
      log.info("This is a partial reset, the shared state will be preserve");
      globalState.setSharedState(currentState.getGlobal().getSharedState());
    }

    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(
            new AirbyteStateMessage()
                .withStateType(AirbyteStateType.GLOBAL)
                .withGlobal(globalState));
  }

}
