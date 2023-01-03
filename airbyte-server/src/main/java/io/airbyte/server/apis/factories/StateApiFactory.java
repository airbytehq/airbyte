/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis.factories;

import io.airbyte.server.apis.StateApiController;
import io.airbyte.server.handlers.StateHandler;
import org.glassfish.hk2.api.Factory;

public class StateApiFactory implements Factory<StateApiController> {

  private static StateHandler stateHandler;

  public static void setValues(final StateHandler stateHandler) {
    StateApiFactory.stateHandler = stateHandler;
  }

  @Override
  public StateApiController provide() {
    return new StateApiController(StateApiFactory.stateHandler);
  }

  @Override
  public void dispose(final StateApiController instance) {
    /* no op */
  }

}
