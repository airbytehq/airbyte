/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination_async.state;

import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

public class FlushFailure {

  private final AtomicBoolean isFailed = new AtomicBoolean(false);

  private final AtomicReference<Exception> exceptionAtomicReference = new AtomicReference<>();

  public void propagateException(Exception e) {
    this.isFailed.set(true);
    this.exceptionAtomicReference.set(e);
  }

  public boolean isFailed() {
    return isFailed.get();
  }

  public Exception getException() {
    return exceptionAtomicReference.get();
  }

}
