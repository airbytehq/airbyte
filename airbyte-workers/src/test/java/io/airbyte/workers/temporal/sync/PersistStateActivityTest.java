/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.temporal.sync;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.features.FeatureFlags;
import io.airbyte.commons.json.Jsons;
import io.airbyte.config.StandardSyncOutput;
import io.airbyte.config.State;
import io.airbyte.config.StateWrapper;
import io.airbyte.config.persistence.StatePersistence;
import java.io.IOException;
import java.util.UUID;
import org.elasticsearch.common.collect.Map;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.junit.jupiter.MockitoExtension;

@ExtendWith(MockitoExtension.class)
public class PersistStateActivityTest {

  private final static UUID CONNECTION_ID = UUID.randomUUID();

  @Mock
  StatePersistence statePersistence;

  @Mock
  FeatureFlags featureFlags;

  @InjectMocks
  PersistStateActivityImpl persistStateActivity;

  @Test
  public void testPersistEmpty() {
    persistStateActivity.persist(CONNECTION_ID, new StandardSyncOutput());

    Mockito.verifyNoInteractions(statePersistence);
  }

  @Test
  public void testPersist() throws IOException {
    Mockito.when(featureFlags.useStreamCapableState()).thenReturn(true);

    final JsonNode jsonState = Jsons.jsonNode(Map.ofEntries(
        Map.entry("some", "state")));

    final State state = new State().withState(jsonState);

    persistStateActivity.persist(CONNECTION_ID, new StandardSyncOutput().withState(state));

    // The ser/der of the state into a state wrapper is tested in StateMessageHelperTest
    Mockito.verify(statePersistence).updateOrCreateState(Mockito.eq(CONNECTION_ID), Mockito.any(StateWrapper.class));
  }

}
