/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.config.StateType;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.config.persistence.StatePersistence;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.protocol.models.StreamDescriptor;
import java.io.IOException;
import java.util.List;
import java.util.Optional;
import java.util.UUID;
import lombok.AllArgsConstructor;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@AllArgsConstructor
public class PersistStateActivityImpl implements PersistStateActivity {

  private final StatePersistence statePersistence;
  private final FeatureFlags featureFlags;
  private static final Logger LOGGER = LoggerFactory.getLogger(PersistStateActivityImpl.class);

  @Override
  public boolean persist(final UUID connectionId, final StandardSyncOutput syncOutput) {
    final State state = syncOutput.getState();
    if (state != null) {
      try {
        final Optional<StateWrapper> maybeStateWrapper = StateMessageHelper.getTypedState(state.getState(), featureFlags.useStreamCapableState());
        if (maybeStateWrapper.isPresent()) {
          final StateType currentStateType = maybeStateWrapper.get().getStateType();
          if (statePersistence.isMigration(connectionId, currentStateType)) {
            validateStreamStates(maybeStateWrapper.get(), syncOutput.getOutputCatalog());
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

  private static void validateStreamStates(final StateWrapper state, final ConfiguredAirbyteCatalog configuredCatalog) {
    final List<StreamDescriptor> stateStreamDescriptors =
        state.getStateMessages().stream().map(stateMessage -> stateMessage.getStream().getStreamDescriptor()).toList();
    configuredCatalog.getStreams().forEach(stream -> {
      final StreamDescriptor streamDescriptor = new StreamDescriptor().withName(stream.getStream().getName())
          .withNamespace(stream.getStream().getNamespace());
      if (!stateStreamDescriptors.contains(streamDescriptor)) {
        throw new IllegalStateException(
            "Job ran during migration from Legacy State to Per Stream State. This job must be retried in order to properly store state.");
      }
    });
  }

}
