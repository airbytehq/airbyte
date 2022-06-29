/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.config.persistence.StatePersistence;
import java.io.IOException;
import java.util.Optional;
import java.util.UUID;
import lombok.AllArgsConstructor;

@AllArgsConstructor
public class PersistStateActivityImpl implements PersistStateActivity {

  private final StatePersistence statePersistence;
  private final FeatureFlags featureFlags;

  @Override
  public boolean persist(final UUID connectionId, final StandardSyncOutput syncOutput) {
    final State state = syncOutput.getState();
    if (state != null) {
      try {
        final Optional<StateWrapper> maybeStateWrapper = StateMessageHelper.getTypedState(state.getState(), featureFlags.useStreamCapableState());
        if (maybeStateWrapper.isPresent()) {
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

}
