/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.concurrency;

import io.airbyte.commons.functional.CheckedConsumer;
import java.util.concurrent.Callable;

public class LifecycledCallable<T> implements Callable<T> {

  public static class Builder<T> {

    private final Callable<T> callable;

    private VoidCallable onStart;
    private CheckedConsumer<T, Exception> onSuccess;
    private CheckedConsumer<Exception, Exception> onException;
    private VoidCallable onFinish;

    public Builder(final Callable<T> callable) {
      this.callable = callable;

      this.onStart = () -> {};
      this.onSuccess = noop -> {};
      this.onException = noop -> {};
      this.onFinish = () -> {};
    }

    public Builder<T> setOnStart(final VoidCallable onStart) {
      this.onStart = onStart;
      return this;
    }

    public Builder<T> setOnSuccess(final CheckedConsumer<T, Exception> onSuccess) {
      this.onSuccess = onSuccess;
      return this;
    }

    public Builder<T> setOnException(final CheckedConsumer<Exception, Exception> onException) {
      this.onException = onException;
      return this;
    }

    public Builder<T> setOnFinish(final VoidCallable onFinish) {
      this.onFinish = onFinish;
      return this;
    }

    public LifecycledCallable<T> build() {
      return new LifecycledCallable<>(onStart, callable, onSuccess, onException, onFinish);
    }

  }

  private final VoidCallable onStart;
  private final Callable<T> decoratedCallable;
  private final CheckedConsumer<T, Exception> onSuccess;
  private final CheckedConsumer<Exception, Exception> onException;
  private final VoidCallable onFinish;

  private LifecycledCallable(final VoidCallable onStart,
                             final Callable<T> decoratedCallable,
                             final CheckedConsumer<T, Exception> onSuccess,
                             final CheckedConsumer<Exception, Exception> onException,
                             final VoidCallable onFinish) {
    this.onStart = onStart;
    this.decoratedCallable = decoratedCallable;
    this.onSuccess = onSuccess;
    this.onException = onException;
    this.onFinish = onFinish;
  }

  @Override
  public T call() throws Exception {
    try {
      onStart();
      final T result = execute();
      onSuccess(result);
      return result;
    } catch (final Exception e) {
      onException(e);
      throw e;
    } finally {
      onFinish();
    }
  }

  private void onStart() throws Exception {
    this.onStart.call();
  }

  private T execute() throws Exception {
    return this.decoratedCallable.call();

  }

  private void onSuccess(final T value) throws Exception {
    this.onSuccess.accept(value);
  }

  private void onException(final Exception e) throws Exception {
    this.onException.accept(e);
  }

  private void onFinish() throws Exception {
    this.onFinish.call();
  }

}
