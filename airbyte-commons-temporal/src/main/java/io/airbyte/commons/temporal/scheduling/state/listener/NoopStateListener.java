/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.temporal.scheduling.state.listener;

import java.util.LinkedList;
import java.util.Queue;
import java.util.UUID;

public class NoopStateListener implements WorkflowStateChangedListener {

  @Override
  public Queue<ChangedStateEvent> events(final UUID id) {
    return new LinkedList<>();
  }

  @Override
  public void addEvent(final UUID id, final ChangedStateEvent event) {}

}
