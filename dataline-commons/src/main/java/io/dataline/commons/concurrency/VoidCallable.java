package io.dataline.commons.concurrency;

import java.util.concurrent.Callable;

public interface VoidCallable extends Callable<Void> {

  default @Override Void call() throws Exception {
    voidCall();
    return null;
  }

  void voidCall() throws Exception;
}
