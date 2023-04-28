package io.airbyte.integrations.destination.record_buffer;

import java.util.concurrent.Callable;

public class StateAcknowledgementTask implements Callable<Void> {

  @Override
  public Void call() throws Exception {
    return null;
  }
}
