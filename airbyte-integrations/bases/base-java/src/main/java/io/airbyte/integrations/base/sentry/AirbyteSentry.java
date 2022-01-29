package io.airbyte.integrations.base.sentry;

import io.sentry.ISpan;
import io.sentry.Sentry;
import io.sentry.SpanStatus;
import java.util.concurrent.Callable;

public class AirbyteSentry {

  @FunctionalInterface
  public interface ThrowingRunnable {
    void call() throws Exception;
  }

  public static void runWithSpan(final String operation, final ThrowingRunnable command) throws Exception {
    final ISpan span = Sentry.getSpan();
    final ISpan childSpan;
    if (span == null) {
      childSpan = Sentry.startTransaction("ROOT", operation);
    } else {
      childSpan = span.startChild(operation);
    }
    try {
      command.call();
      childSpan.finish(SpanStatus.OK);
    } catch (final Exception e) {
      childSpan.setThrowable(e);
      childSpan.finish(SpanStatus.INTERNAL_ERROR);
      throw e;
    } finally {
      childSpan.finish();
    }
  }

  public static <T> T runWithSpan(final String operation, final Callable<T> command) throws Exception {
    final ISpan span = Sentry.getSpan();
    final ISpan childSpan;
    if (span == null) {
      childSpan = Sentry.startTransaction("ROOT", operation);
    } else {
      childSpan = span.startChild(operation);
    }
    try {
      final T result = command.call();
      childSpan.finish(SpanStatus.OK);
      return result;
    } catch (final Exception e) {
      childSpan.setThrowable(e);
      childSpan.finish(SpanStatus.INTERNAL_ERROR);
      throw e;
    } finally {
      childSpan.finish();
    }
  }

}
