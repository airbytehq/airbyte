/*
 * MIT License
 *
 * Copyright (c) 2020 Dataline
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.dataline.commons.concurrency;

import io.dataline.commons.functional.CheckedFunction;
import java.util.concurrent.Callable;
import java.util.function.Consumer;

public class LifecycledCallable<T> implements Callable<T> {

  public static class Builder<T> {

    private final Callable<T> callable;

    private VoidCallable onStart;
    private CheckedFunction<T, T, Exception> onSuccess;
    private Consumer<Exception> onException;
    private VoidCallable onFinish;

    public Builder(final Callable<T> callable) {
      this.callable = callable;

      this.onStart = () -> {};
      this.onSuccess = e -> e;
      this.onException = noop -> {};
      this.onFinish = () -> {};
    }

    public Builder<T> setOnStart(VoidCallable onStart) {
      this.onStart = onStart;
      return this;
    }

    public Builder<T> setOnSuccess(CheckedFunction<T, T, Exception> onSuccess) {
      this.onSuccess = onSuccess;
      return this;
    }

    public Builder<T> setOnException(Consumer<Exception> onException) {
      this.onException = onException;
      return this;
    }

    public Builder<T> setOnFinish(VoidCallable onFinish) {
      this.onFinish = onFinish;
      return this;
    }

    public LifecycledCallable<T> build() {
      return new LifecycledCallable<>(onStart, callable, onSuccess, onException, onFinish);
    }

  }

  private final VoidCallable onStart;
  private final Callable<T> decoratedCallable;
  private final CheckedFunction<T, T, Exception> onSuccess;
  private final Consumer<Exception> onException;
  private final VoidCallable onFinish;

  private LifecycledCallable(final VoidCallable onStart,
                             final Callable<T> decoratedCallable,
                             final CheckedFunction<T, T, Exception> onSuccess,
                             final Consumer<Exception> onException,
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
      return onSuccess(execute());
    } catch (Exception e) {
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

  private T onSuccess(T value) throws Exception {
    return this.onSuccess.apply(value);
  }

  private void onException(Exception e) {
    this.onException.accept(e);
  }

  private void onFinish() throws Exception {
    this.onFinish.call();
  }

}
