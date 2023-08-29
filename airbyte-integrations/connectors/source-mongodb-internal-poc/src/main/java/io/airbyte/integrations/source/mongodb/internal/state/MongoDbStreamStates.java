/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mongodb.internal.state;

import java.util.Comparator;
import java.util.List;
import java.util.Optional;

public record MongoDbStreamStates(List<MongoDbStreamState> states) {
  static private final Comparator<MongoDbStreamState> idComparator = Comparator.comparing(MongoDbStreamState::idType);

  public Optional<MongoDbStreamState> getNextInProgress() {
    return states.stream()
        .sorted(idComparator)
        .filter(state -> state.status() == InitialSnapshotStatus.IN_PROGRESS).findFirst();
  }
}
