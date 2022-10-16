/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.lang;

import java.util.concurrent.Callable;
import java.util.function.Function;
import lombok.extern.slf4j.Slf4j;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Slf4j
public class Exceptions {

  private static final Logger LOGGER = LoggerFactory.getLogger(Exceptions.class);

  /**
   * Catch a checked exception and rethrow as a {@link RuntimeException}
   *
   * @param callable - function that throws a checked exception.
   * @param <T> - return type of the function.
   * @return object that the function returns.
   */
  public static <T> T toRuntime(final Callable<T> callable) {
    try {
      return callable.call();
    } catch (final RuntimeException e) {
      throw e;
    } catch (final Exception e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * Catch a checked exception and rethrow as a {@link RuntimeException}.
   *
   * @param voidCallable - function that throws a checked exception.
   */
  public static void toRuntime(final Procedure voidCallable) {
    castCheckedToRuntime(voidCallable, RuntimeException::new);
  }

  public static void toIllegalState(final Procedure voidCallable) {
    castCheckedToRuntime(voidCallable, IllegalStateException::new);
  }

  public static void toIllegalArgument(final Procedure voidCallable) {
    castCheckedToRuntime(voidCallable, IllegalArgumentException::new);
  }

  private static void castCheckedToRuntime(final Procedure voidCallable, final Function<Exception, RuntimeException> exceptionFactory) {
    try {
      voidCallable.call();
    } catch (final RuntimeException e) {
      throw e;
    } catch (final Exception e) {
      throw exceptionFactory.apply(e);
    }
  }

  public static void swallow(final Procedure procedure) {
    try {
      procedure.call();
    } catch (final Exception e) {
      LOGGER.error("Swallowed error.", e);
    }
  }

  public interface Procedure {

    void call() throws Exception;

  }

  public static <T> T swallowWithDefault(final Callable<T> procedure, final T defaultValue) {
    try {
      return procedure.call();
    } catch (Exception e) {
      return defaultValue;
    }
  }

}
