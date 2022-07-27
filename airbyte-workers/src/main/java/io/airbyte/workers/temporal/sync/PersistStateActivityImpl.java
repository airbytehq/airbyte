/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import com.google.common.annotations.VisibleForTesting;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.protocol.models.CatalogHelpers;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.StreamDescriptor;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class PersistStateActivityImpl implements PersistStateActivity {

  private final StatePersistence statePersistence;
  private final FeatureFlags featureFlags;

  @Override
  public boolean persist(final UUID connectionId, final StandardSyncOutput syncOutput, final ConfiguredAirbyteCatalog configuredCatalog) {
    final State state = syncOutput.getState();
    if (state != null) {
      try {
        final Optional<StateWrapper> maybeStateWrapper = StateMessageHelper.getTypedState(state.getState(), featureFlags.useStreamCapableState());
        if (maybeStateWrapper.isPresent()) {
          final Optional<StateWrapper> previousState = statePersistence.getCurrentState(connectionId);
          final StateType newStateType = maybeStateWrapper.get().getStateType();
          if (statePersistence.isMigration(connectionId, newStateType, previousState) && newStateType == StateType.STREAM) {
            validateStreamStates(maybeStateWrapper.get(), configuredCatalog);
          }

          statePersistence.updateOrCreateState(connectionId, maybeStateWrapper.get());
        }
      } catch (final IOException e) {
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
