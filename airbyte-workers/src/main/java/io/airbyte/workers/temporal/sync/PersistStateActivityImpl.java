/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import static io.airbyte.config.helpers.StateMessageHelper.isMigration;
import static io.airbyte.workers.helper.StateConverter.convertClientStateTypeToInternal;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.ConnectionIdRequestBody;
import io.airbyte.api.client.model.generated.ConnectionState;
import io.airbyte.api.client.model.generated.ConnectionStateCreateOrUpdate;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.StreamDescriptor;
import io.airbyte.workers.helper.StateConverter;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class PersistStateActivityImpl implements PersistStateActivity {

  private final AirbyteApiClient airbyteApiClient;
  private final FeatureFlags featureFlags;

  @Override
  public boolean persist(final UUID connectionId, final StandardSyncOutput syncOutput, final ConfiguredAirbyteCatalog configuredCatalog) {
    final State state = syncOutput.getState();
    if (state != null) {
      // todo: these validation logic should happen on server side.
      try {
        final Optional<StateWrapper> maybeStateWrapper = StateMessageHelper.getTypedState(state.getState(), featureFlags.useStreamCapableState());
        if (maybeStateWrapper.isPresent()) {
          final ConnectionState previousState = airbyteApiClient.getConnectionApi()
              .getState(new ConnectionIdRequestBody().connectionId(connectionId));
          if (previousState != null) {
            final StateType newStateType = maybeStateWrapper.get().getStateType();
            final StateType prevStateType = convertClientStateTypeToInternal(previousState.getStateType());

            if (isMigration(newStateType, prevStateType) && newStateType == StateType.STREAM) {
              validateStreamStates(maybeStateWrapper.get(), configuredCatalog);
            }
          }

          airbyteApiClient.getConnectionApi().createOrUpdateState(
              new ConnectionStateCreateOrUpdate()
                  .connectionId(connectionId)
                  .connectionState(StateConverter.toClient(connectionId, maybeStateWrapper.orElse(null))));
        }
      } catch (final ApiException e) {
        throw new RuntimeException(e);
      }
      return true;
    } else {
      return false;
    }
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
