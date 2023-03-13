package io.airbyte.integrations.util;

import java.util.concurrent.ConcurrentLinkedQueue;

/**
 * Now that certain parts of the Destination process are async, we need a way to pass
 * Exceptions as a signal back to the main thread. This will typically be used to detect
 * the presence of fatal errors and shut down processing.
 *
 * This is a singleton to make it easy to access from within any part of the Destination
 * code base. Could be used in other "applications", however.
 */
public class ErrorChannel {

  private static final ErrorChannel instance = new ErrorChannel();

  private final ConcurrentLinkedQueue<Exception> queue = new ConcurrentLinkedQueue<>();

  public static ErrorChannel getInstance() {
    return instance;
  }

  private ErrorChannel() {}

  public boolean hasError() {
    return !queue.isEmpty();
  }

  public void addError(Exception e) {
    queue.add(e);
  }

  public Exception getNextError() {
    return queue.poll();
  }
}
