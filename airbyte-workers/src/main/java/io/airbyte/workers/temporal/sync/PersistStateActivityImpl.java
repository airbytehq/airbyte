/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static io.airbyte.config.helpers.StateMessageHelper.isMigration;
import static io.airbyte.metrics.lib.ApmTraceConstants.ACTIVITY_TRACE_OPERATION_NAME;
import static io.airbyte.metrics.lib.ApmTraceConstants.Tags.CONNECTION_ID_KEY;
import static io.airbyte.workers.helper.StateConverter.convertClientStateTypeToInternal;

import com.google.common.annotations.VisibleForTesting;
import datadog.trace.api.Trace;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.ConnectionState;
import io.airbyte.api.client.model.generated.ConnectionStateCreateOrUpdate;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.workers.helper.StateConverter;
import jakarta.inject.Singleton;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Singleton
public class PersistStateActivityImpl implements PersistStateActivity {

  private final AirbyteApiClient airbyteApiClient;
  private final FeatureFlags featureFlags;

  public PersistStateActivityImpl(final AirbyteApiClient airbyteApiClient, final FeatureFlags featureFlags) {
    this.airbyteApiClient = airbyteApiClient;
    this.featureFlags = featureFlags;
  }

  @Trace(operationName = ACTIVITY_TRACE_OPERATION_NAME)
  @Override
  public boolean persist(final UUID connectionId, final StandardSyncOutput syncOutput, final ConfiguredAirbyteCatalog configuredCatalog) {
    ApmTraceUtils.addTagsToTrace(Map.of(CONNECTION_ID_KEY, connectionId.toString()));
    final State state = syncOutput.getState();
    if (state != null) {
      // todo: these validation logic should happen on server side.
      try {
        final Optional<StateWrapper> maybeStateWrapper = StateMessageHelper.getTypedState(state.getState(), featureFlags.useStreamCapableState());
        if (maybeStateWrapper.isPresent()) {
          final ConnectionState previousState =
              AirbyteApiClient.retryWithJitter(
                  () -> airbyteApiClient.getStateApi().getState(new ConnectionIdRequestBody().connectionId(connectionId)),
                  "get state");

          validate(configuredCatalog, maybeStateWrapper, previousState);

          AirbyteApiClient.retryWithJitter(
              () -> {
                airbyteApiClient.getStateApi().createOrUpdateState(
                    new ConnectionStateCreateOrUpdate()
                        .connectionId(connectionId)
                        .connectionState(StateConverter.toClient(connectionId, maybeStateWrapper.orElse(null))));
                return null;
              },
              "create or update state");
        }
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
      return true;
    } else {
      return false;
    }
  }

  /**
   * Validates whether it is safe to persist the new state based on the previously saved state.
   *
   * @param configuredCatalog The configured catalog of streams for the connection.
   * @param newState The new state.
   * @param previousState The previous state.
   */
  private void validate(final ConfiguredAirbyteCatalog configuredCatalog,
                        final Optional<StateWrapper> newState,
                        final ConnectionState previousState) {
    /**
     * If state validation is enabled and the previous state exists and is not empty, make sure that
     * state will not be lost as part of the migration from legacy -> per stream.
     *
     * Otherwise, it is okay to update if the previous state is missing or empty.
     */
    if (featureFlags.needStateValidation() && !isStateEmpty(previousState)) {
      final StateType newStateType = newState.get().getStateType();
      final StateType prevStateType = convertClientStateTypeToInternal(previousState.getStateType());

      if (isMigration(newStateType, prevStateType) && newStateType == StateType.STREAM) {
        validateStreamStates(newState.get(), configuredCatalog);
      }
    }
  }

  /**
   * Test whether the connection state is empty.
   *
   * @param connectionState The connection state.
   * @return {@code true} if the connection state is null or empty, {@code false} otherwise.
   */
  private boolean isStateEmpty(final ConnectionState connectionState) {
    return connectionState == null || connectionState.getState() == null || connectionState.getState().isEmpty();
  }

  @VisibleForTesting
  void validateStreamStates(final StateWrapper state, final ConfiguredAirbyteCatalog configuredCatalog) {
    final List<StreamDescriptor> stateStreamDescriptors =
        state.getStateMessages().stream().map(stateMessage -> stateMessage.getStream().getStreamDescriptor()).toList();
    final List<StreamDescriptor> catalogStreamDescriptors = CatalogHelpers.extractIncrementalStreamDescriptors(configuredCatalog);
    catalogStreamDescriptors.forEach(streamDescriptor -> {
      if (!stateStreamDescriptors.contains(streamDescriptor)) {
        throw new IllegalStateException(
            "Job ran during migration from Legacy State to Per Stream State. One of the streams that did not have state is: " + streamDescriptor
                + ". Job must be retried in order to properly store state.");
      }
    });
  }

}
