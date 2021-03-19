/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
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
