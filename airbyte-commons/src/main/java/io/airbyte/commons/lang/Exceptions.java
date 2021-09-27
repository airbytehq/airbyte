/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.lang;

import java.util.concurrent.Callable;
import java.util.function.Function;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class Exceptions {

  private static final Logger LOGGER = LoggerFactory.getLogger(Exceptions.class);

  /**
   * Catch a checked exception and rethrow as a {@link RuntimeException}
   *
   * @param callable - function that throws a checked exception.
   * @param <T> - return type of the function.
   * @return object that the function returns.
   */
  public static <T> T toRuntime(Callable<T> callable) {
    try {
      return callable.call();
    } catch (RuntimeException e) {
      throw e;
    } catch (Exception e) {
      throw new RuntimeException(e);
    }
  }

  /**
   * Catch a checked exception and rethrow as a {@link RuntimeException}.
   *
   * @param voidCallable - function that throws a checked exception.
   */
  public static void toRuntime(Procedure voidCallable) {
    castCheckedToRuntime(voidCallable, RuntimeException::new);
  }

  public static void toIllegalState(Procedure voidCallable) {
    castCheckedToRuntime(voidCallable, IllegalStateException::new);
  }

  public static void toIllegalArgument(Procedure voidCallable) {
    castCheckedToRuntime(voidCallable, IllegalArgumentException::new);
  }

  private static void castCheckedToRuntime(Procedure voidCallable, Function<Exception, RuntimeException> exceptionFactory) {
    try {
      voidCallable.call();
    } catch (RuntimeException e) {
      throw e;
    } catch (Exception e) {
      throw exceptionFactory.apply(e);
    }
  }

  public static void swallow(Procedure procedure) {
    try {
      procedure.call();
    } catch (Exception e) {
      LOGGER.error("Swallowed error.", e);
    }
  }

  public interface Procedure {

    void call() throws Exception;

  }

}
