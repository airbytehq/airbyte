/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ResetSourceConfiguration;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.StreamDescriptor;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.protocol.models.AirbyteGlobalState;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.EmptyStackException;
import java.util.HashSet;
import java.util.LinkedList;
import java.util.Optional;
import java.util.Queue;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Collectors;
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
  private Optional<StateWrapper> stateWrapper;

  public EmptyAirbyteSource() {
    hasEmittedState = new AtomicBoolean();
  }

  @Override
  public void start(final WorkerSourceConfig sourceConfig, final Path jobRoot) throws Exception {

    try {
      if (sourceConfig == null || sourceConfig.getSourceConnectionConfiguration() == null) {
        isPartialReset = false;
      } else {
        final ResetSourceConfiguration sourceConfiguration =
            Jsons.object(sourceConfig.getSourceConnectionConfiguration(), ResetSourceConfiguration.class);
        streamDescriptors.addAll(sourceConfiguration.getStreamsToReset());
        if (streamDescriptors.isEmpty()) {
          // TODO: This is done to be able to handle the transition period where we can have no stream being pass to the configuration because the
          //  logic of populating this list is not implemented
          isPartialReset = false;
        } else {
          stateWrapper = StateMessageHelper.getTypedState(sourceConfig.getState().getState());

          if (stateWrapper.isPresent() &&
              stateWrapper.get().getStateType() == StateType.LEGACY &&
              !configHasFullCatalog(sourceConfig)) {
            log.error("The state a legacy one but we are trying to do a partial update, this is not supported.");
            throw new IllegalStateException("Try to perform a partial reset on a legacy state");
          }

          isPartialReset = true;
        }
      }
    } catch (final IllegalArgumentException e) {
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
      if (stateWrapper.get().getStateType() == StateType.STREAM) {
        return emitStreamState();
      } else {
        return emitGlobalState();
      }
    } else {
      return emitLegacyState();
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

  private Optional<AirbyteMessage> emitStreamState() {
    // Per stream, it will emit one message per stream being reset
    if (!streamDescriptors.isEmpty()) {
      try {
        final StreamDescriptor streamDescriptor = streamDescriptors.poll();
        return Optional.of(getNullStreamStateMessage(streamDescriptor));
      } catch (final EmptyStackException e) {
        return Optional.empty();
      }
    } else {
      return Optional.empty();
    }
  }

  private Optional<AirbyteMessage> emitGlobalState() {
    if (hasEmittedState.get()) {
      return Optional.empty();
    } else {
      hasEmittedState.compareAndSet(false, true);
      return Optional.of(getNullGlobalMessage(streamDescriptors, stateWrapper.get().getGlobal()));
    }
  }

  private Optional<AirbyteMessage> emitLegacyState() {
    if (!hasEmittedState.get()) {
      hasEmittedState.compareAndSet(false, true);
      return Optional.of(new AirbyteMessage().withType(Type.STATE)
          .withState(new AirbyteStateMessage().withStateType(AirbyteStateType.LEGACY).withData(Jsons.emptyObject())));
    } else {
      return Optional.empty();
    }
  }

  private boolean configHasFullCatalog(final WorkerSourceConfig sourceConfig) {
    final Set<StreamDescriptor> catalogStreamDescriptors = sourceConfig.getCatalog().getStreams().stream().map(
            configuredAirbyteStream -> new StreamDescriptor()
                .withName(configuredAirbyteStream.getStream().getName())
                .withNamespace(configuredAirbyteStream.getStream().getNamespace()))
        .collect(Collectors.toSet());
    final Set<StreamDescriptor> configStreamDescriptors = new HashSet<>(streamDescriptors);

    return catalogStreamDescriptors.equals(configStreamDescriptors);
  }

  private AirbyteMessage getNullStreamStateMessage(final StreamDescriptor configStreamDescriptor) {
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

  private AirbyteMessage getNullGlobalMessage(final Queue<StreamDescriptor> configStreamDescriptors, final AirbyteStateMessage currentState) {
    final AirbyteGlobalState globalState = new AirbyteGlobalState();
    globalState.setStreamStates(new ArrayList<>());

    currentState.getGlobal().getStreamStates().forEach(exitingState -> globalState.getStreamStates()
        .add(
            new AirbyteStreamState()
                .withStreamDescriptor(exitingState.getStreamDescriptor())
                .withStreamState(
                    configStreamDescriptors.contains(new StreamDescriptor()
                        .withName(exitingState.getStreamDescriptor().getName())
                        .withNamespace(exitingState.getStreamDescriptor().getNamespace())) ? null : exitingState.getStreamState())));

    // If all the stream in the current state have been reset, we consider to shared as reset as well
    if (currentState.getGlobal().getStreamStates().size() == globalState.getStreamStates().stream()
        .filter(streamState -> streamState.getStreamState() == null).count()) {
      log.info("All the streams of a global state have been reset, the shared state will be erased as well");
      globalState.setSharedState(null);
    } else {
      log.info("This is a partial reset, the shared state will be preserve");
      globalState.setSharedState(currentState.getGlobal().getSharedState());
    }

    // Add state being reset that are not in the current state. This is made to follow the contract of
    // the global state always containing the entire
    // state
    configStreamDescriptors.forEach(configStreamDescriptor -> {
      if (!currentState.getGlobal().getStreamStates().stream().map(streamState -> streamState.getStreamDescriptor()).toList()
          .contains(new io.airbyte.protocol.models.StreamDescriptor()
              .withName(configStreamDescriptor.getName())
              .withNamespace(configStreamDescriptor.getNamespace()))) {
        globalState.getStreamStates().add(new AirbyteStreamState()
            .withStreamDescriptor(new io.airbyte.protocol.models.StreamDescriptor()
                .withName(configStreamDescriptor.getName())
                .withNamespace(configStreamDescriptor.getNamespace()))
            .withStreamState(null));
      }
    });

    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(
            new AirbyteStateMessage()
                .withStateType(AirbyteStateType.GLOBAL)
                .withGlobal(globalState));
  }

}
