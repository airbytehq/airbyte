/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.util;

import org.slf4j.LoggerFactory;

import java.util.Iterator;

/**
 * If you operate on this iterator, you better close it. {@link AutoCloseableIterator#close} must be
 * idempotent. The contract on this interface is that it may be called MANY times.
 * <p>
 * Futher, in the close case, we do not propagate exceptions since:
 * <li>- we cannot take any relevant actions.</li>
 * <li>- as of this comment, there is no discernible impact as jobs run on containerized infrastructure.</li>
 *
 * @param <T> type
 */
public interface AutoCloseableIterator<T> extends Iterator<T>, AutoCloseable, AirbyteStreamAware {
  default void logWarn(String message, Throwable t) {
    LoggerFactory.getLogger(AutoCloseableIterator.class).warn(message, t);
  }

  @Override
  default void close() throws Exception {
    try {
      closeSafely();
    } catch (Exception e) {
      logWarn("Exception ignored during AutoCloseableIterator closing: {}", e);
    }
  }

  /**
   * Concrete implementations should implement this method with their closing logic.
   */
  void closeSafely() throws Exception;

}
