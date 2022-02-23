/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.workers.protocols;

import io.airbyte.config.State;
import java.util.Optional;
import java.util.function.Consumer;

public interface MessageTracker<T> extends Consumer<T> {

  @Override
  void accept(T message);

  long getRecordCount();

  long getBytesCount();

  Optional<State> getOutputState();

}
