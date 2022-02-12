/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.sentry;

import io.sentry.ISpan;
import io.sentry.Sentry;
import io.sentry.SpanStatus;
import java.util.Collections;
import java.util.Map;
import org.apache.logging.log4j.util.Strings;

public class AirbyteSentry {

  private static final String DEFAULT_ROOT_TRANSACTION = "ROOT";
  private static final String DEFAULT_UNKNOWN_OPERATION = "ANONYMOUS";

  @FunctionalInterface
  public interface ThrowingRunnable<E extends Exception> {

    void call() throws E;

  }

  @FunctionalInterface
  public interface ThrowingCallable<T, E extends Exception> {

    T call() throws E;

  }

  /**
   * Run an operation and profile it with Sentry. The operation will run in a span under the current
   * Sentry transaction. If no transaction exists, a default one will be created.
   */
  public static <E extends Exception> void executeWithTracing(final String name, final ThrowingRunnable<E> command) throws E {
    executeWithTracing(name, command, Collections.emptyMap());
  }

  /**
   * Run an operation and profile it with Sentry. The operation will run in a span under the current
   * Sentry transaction. If no transaction exists, a default one will be created.
   *
   * @param metadata Extra data about this operation. For example: { "stream": "table1",
   *        "recordCount": 1000 }.
   */
  public static <E extends Exception> void executeWithTracing(final String name,
                                                              final ThrowingRunnable<E> command,
                                                              final Map<String, Object> metadata)
      throws E {
    final ISpan childSpan = createChildSpan(Sentry.getSpan(), name, metadata);
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

  /**
   * Run an operation and profile it with Sentry. The operation will run in a span under the current
   * Sentry transaction. If no transaction exists, a default one will be created.
   */
  public static <T, E extends Exception> T queryWithTracing(final String name, final ThrowingCallable<T, E> command) throws E {
    return queryWithTracing(name, command, Collections.emptyMap());
  }

  /**
   * Run an operation and profile it with Sentry. The operation will run in a span under the current
   * Sentry transaction. If no transaction exists, a default one will be created.
   *
   * @param metadata Extra data about this operation. For example: { "stream": "table1",
   *        "recordCount": 1000 }.
   */
  public static <T, E extends Exception> T queryWithTracing(final String name,
                                                            final ThrowingCallable<T, E> command,
                                                            final Map<String, Object> metadata)
      throws E {
    final ISpan childSpan = createChildSpan(Sentry.getSpan(), name, metadata);
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

  private static ISpan createChildSpan(final ISpan currentSpan, final String operationName, final Map<String, Object> metadata) {
    final String name = Strings.isBlank(operationName) ? DEFAULT_UNKNOWN_OPERATION : operationName;
    final ISpan childSpan;
    if (currentSpan == null) {
      childSpan = Sentry.startTransaction(DEFAULT_ROOT_TRANSACTION, operationName);
    } else {
      childSpan = currentSpan.startChild(operationName);
    }
    if (metadata != null && !metadata.isEmpty()) {
      metadata.forEach(childSpan::setData);
    }
    return childSpan;
  }

}
