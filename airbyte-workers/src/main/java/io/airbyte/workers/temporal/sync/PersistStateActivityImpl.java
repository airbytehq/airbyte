/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import io.airbyte.api.client.AirbyteApiClient;
import io.airbyte.api.client.invoker.generated.ApiException;
import io.airbyte.api.client.model.generated.ConnectionStateCreateOrUpdate;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.helpers.StateMessageHelper;
import io.airbyte.protocol.models.ConfiguredAirbyteCatalog;
import io.airbyte.workers.helper.StateConverter;
import jakarta.inject.Singleton;
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

  @Override
  public boolean persist(final UUID connectionId, final StandardSyncOutput syncOutput, final ConfiguredAirbyteCatalog configuredCatalog) {
    final State state = syncOutput.getState();
    if (state != null) {
      // todo: these validation logic should happen on server side.
      try {
        final Optional<StateWrapper> maybeStateWrapper = StateMessageHelper.getTypedState(state.getState(), featureFlags.useStreamCapableState());
        if (maybeStateWrapper.isPresent()) {
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

}
