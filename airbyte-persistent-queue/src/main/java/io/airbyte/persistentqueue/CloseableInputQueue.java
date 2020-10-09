package io.airbyte.persistentqueue;

import java.util.Queue;

public interface CloseableInputQueue<E> extends Queue<E>, AutoCloseable {

  /**
   * Calling this signals that no more records will be written to the queue by ANY thread.
   */
  void closeInput();
}
