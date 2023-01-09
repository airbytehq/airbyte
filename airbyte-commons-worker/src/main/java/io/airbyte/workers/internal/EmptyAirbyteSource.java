/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.internal;

import static io.airbyte.metrics.lib.ApmTraceConstants.WORKER_OPERATION_NAME;

import datadog.trace.api.Trace;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.ResetSourceConfiguration;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.WorkerSourceConfig;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.protocol.models.AirbyteGlobalState;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteStateMessage;
import io.airbyte.protocol.models.AirbyteStateMessage.AirbyteStateType;
import io.airbyte.protocol.models.AirbyteStreamState;
import io.airbyte.protocol.models.StreamDescriptor;
import java.nio.file.Path;
import java.util.ArrayList;
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
  private final Queue<StreamDescriptor> streamsToReset = new LinkedList<>();
  private final boolean useStreamCapableState;
  // TODO: Once we are sure that the legacy way of transmitting the state is not use anymore, we need
  // to remove this variable and the associated
  // checks
  private boolean isResetBasedForConfig;
  private boolean isStarted = false;
  private Optional<StateWrapper> stateWrapper;

  public EmptyAirbyteSource(final boolean useStreamCapableState) {
    hasEmittedState = new AtomicBoolean();
    this.useStreamCapableState = useStreamCapableState;
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public void start(final WorkerSourceConfig workerSourceConfig, final Path jobRoot) throws Exception {

    if (workerSourceConfig == null || workerSourceConfig.getSourceConnectionConfiguration() == null) {
      // TODO: When the jobConfig is fully updated and tested, we can remove this extra check that makes
      // us compatible with running a reset with
      // a null config
      /*
       * This is a protection against reverting a commit that set the resetSourceConfiguration, it makes
       * that there is not side effect of such a revert. The legacy behavior is to have the config as an
       * empty jsonObject, this is an extra protection if the workerConfiguration is null. In the previous
       * implementation it was unused so passing it as null should not result in a NPE or a parsing
       * failure.
       */
      isResetBasedForConfig = false;
    } else {
      final ResetSourceConfiguration resetSourceConfiguration;
      resetSourceConfiguration = parseResetSourceConfigurationAndLogError(workerSourceConfig);
      streamsToReset.addAll(resetSourceConfiguration.getStreamsToReset());

      if (streamsToReset.isEmpty()) {
        // TODO: This is done to be able to handle the transition period where we can have no stream being
        // pass to the configuration because the
        // logic of populating this list is not implemented
        /*
         * This is a protection against reverting a commit that set the resetSourceConfiguration, it makes
         * that there is not side effect of such a revert. The legacy behavior is to have the config as an
         * empty object, it has been changed here:
         * https://github.com/airbytehq/airbyte/pull/13696/files#diff-
         * f51ff997b60a346c704608bb1cd7d22457eda2559b42987d5fa1281d568fc222L40
         */
        isResetBasedForConfig = false;
      } else {
        if (workerSourceConfig.getState() != null) {
          stateWrapper = StateMessageHelper.getTypedState(workerSourceConfig.getState().getState(), useStreamCapableState);

          if (stateWrapper.isPresent() &&
              stateWrapper.get().getStateType() == StateType.LEGACY &&
              !resettingAllCatalogStreams(workerSourceConfig)) {
            log.error("The state a legacy one but we are trying to do a partial update, this is not supported.");
            throw new IllegalStateException("Try to perform a partial reset on a legacy state");
          }

          isResetBasedForConfig = true;
        } else {
          /// No state
          isResetBasedForConfig = false;
        }

      }
    }
    isStarted = true;
  }

  // always finished. it has no data to send.
  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public boolean isFinished() {
    return hasEmittedState.get();
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public int getExitValue() {
    return 0;
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public Optional<AirbyteMessage> attemptRead() {
    if (!isStarted) {
      throw new IllegalStateException("The empty source has not been started.");
    }

    if (isResetBasedForConfig) {
      if (stateWrapper.get().getStateType() == StateType.STREAM) {
        return emitStreamState();
      } else if (stateWrapper.get().getStateType() == StateType.GLOBAL) {
        return emitGlobalState();
      } else {
        return emitLegacyState();
      }
    } else {
      return emitLegacyState();
    }
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public void close() throws Exception {
    // no op.
  }

  @Trace(operationName = WORKER_OPERATION_NAME)
  @Override
  public void cancel() throws Exception {
    // no op.
  }

  private Optional<AirbyteMessage> emitStreamState() {
    // Per stream, it will emit one message per stream being reset
    if (!streamsToReset.isEmpty()) {
      final StreamDescriptor streamDescriptor = streamsToReset.poll();
      return Optional.of(getNullStreamStateMessage(streamDescriptor));
    } else {
      hasEmittedState.compareAndSet(false, true);
      return Optional.empty();
    }
  }

  private Optional<AirbyteMessage> emitGlobalState() {
    if (hasEmittedState.get()) {
      return Optional.empty();
    } else {
      hasEmittedState.compareAndSet(false, true);
      return Optional.of(getNullGlobalMessage(streamsToReset, stateWrapper.get().getGlobal()));
    }
  }

  private Optional<AirbyteMessage> emitLegacyState() {
    if (hasEmittedState.get()) {
      return Optional.empty();
    } else {
      hasEmittedState.compareAndSet(false, true);
      return Optional.of(new AirbyteMessage().withType(Type.STATE)
          .withState(new AirbyteStateMessage().withType(AirbyteStateType.LEGACY).withData(Jsons.emptyObject())));
    }
  }

  private boolean resettingAllCatalogStreams(final WorkerSourceConfig sourceConfig) {
    final Set<StreamDescriptor> catalogStreamDescriptors = sourceConfig.getCatalog().getStreams().stream().map(
        configuredAirbyteStream -> new StreamDescriptor()
            .withName(configuredAirbyteStream.getStream().getName())
            .withNamespace(configuredAirbyteStream.getStream().getNamespace()))
        .collect(Collectors.toSet());
    final Set<StreamDescriptor> streamsToResetDescriptors = new HashSet<>(streamsToReset);
    return streamsToResetDescriptors.containsAll(catalogStreamDescriptors);
  }

  private AirbyteMessage getNullStreamStateMessage(final StreamDescriptor streamsToReset) {
    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(
            new AirbyteStateMessage()
                .withType(AirbyteStateType.STREAM)
                .withStream(
                    new AirbyteStreamState()
                        .withStreamDescriptor(new io.airbyte.protocol.models.StreamDescriptor()
                            .withName(streamsToReset.getName())
                            .withNamespace(streamsToReset.getNamespace()))
                        .withStreamState(null)));
  }

  private AirbyteMessage getNullGlobalMessage(final Queue<StreamDescriptor> streamsToReset, final AirbyteStateMessage currentState) {
    final AirbyteGlobalState globalState = new AirbyteGlobalState();
    globalState.setStreamStates(new ArrayList<>());

    currentState.getGlobal().getStreamStates().forEach(existingState -> globalState.getStreamStates()
        .add(
            new AirbyteStreamState()
                .withStreamDescriptor(existingState.getStreamDescriptor())
                .withStreamState(
                    streamsToReset.contains(new StreamDescriptor()
                        .withName(existingState.getStreamDescriptor().getName())
                        .withNamespace(existingState.getStreamDescriptor().getNamespace())) ? null : existingState.getStreamState())));

    // If all the streams in the current state have been reset, we consider this to be a full reset, so
    // reset the shared state as well
    if (currentState.getGlobal().getStreamStates().size() == globalState.getStreamStates().stream()
        .filter(streamState -> streamState.getStreamState() == null).count()) {
      log.info("All the streams of a global state have been reset, the shared state will be erased as well");
      globalState.setSharedState(null);
    } else {
      log.info("This is a partial reset, the shared state will be preserved");
      globalState.setSharedState(currentState.getGlobal().getSharedState());
    }

    // Add state being reset that are not in the current state. This is made to follow the contract of
    // the global state always containing the entire
    // state
    streamsToReset.forEach(configStreamDescriptor -> {
      final io.airbyte.protocol.models.StreamDescriptor streamDescriptor = new io.airbyte.protocol.models.StreamDescriptor()
          .withName(configStreamDescriptor.getName())
          .withNamespace(configStreamDescriptor.getNamespace());
      if (!currentState.getGlobal().getStreamStates().stream().map(streamState -> streamState.getStreamDescriptor()).toList()
          .contains(streamDescriptor)) {
        globalState.getStreamStates().add(new AirbyteStreamState()
            .withStreamDescriptor(streamDescriptor)
            .withStreamState(null));
      }
    });

    return new AirbyteMessage()
        .withType(Type.STATE)
        .withState(
            new AirbyteStateMessage()
                .withType(AirbyteStateType.GLOBAL)
                .withGlobal(globalState));
  }

  private ResetSourceConfiguration parseResetSourceConfigurationAndLogError(final WorkerSourceConfig workerSourceConfig) {
    try {
      return Jsons.object(workerSourceConfig.getSourceConnectionConfiguration(), ResetSourceConfiguration.class);
    } catch (final IllegalArgumentException e) {
      log.error("The configuration provided to the reset has an invalid format");
      throw e;
    }
  }

}
