/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.base;

import java.util.ArrayList;
import java.util.List;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AirbyteExceptionHandler implements Thread.UncaughtExceptionHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteExceptionHandler.class);
  public static final String logMessage = "Something went wrong in the connector. See the logs for more details.";

  /**
   * If this list is populated, then the exception handler will attempt to deinterpolate the error
   * message before emitting a trace message. This is useful for connectors which (a) emit a single
   * exception class, and (b) rely on that exception's message to distinguish between error types.
   * <p>
   * If this is active, then the trace message will:
   * <ol>
   *   <li>Not contain the stacktrace at all. This causes Sentry to use its fallback grouping
   *   (using exception class and message)</li>
   *   <li>Contain the original exception message as the external message, and a mangled message
   *   as the internal message.</li>
   * </ol>
   */
  public static final List<String> STRINGS_TO_REMOVE = new ArrayList<>();

  @Override
  public void uncaughtException(Thread t, Throwable e) {
    // This is a naive AirbyteTraceMessage emission in order to emit one when any error occurs in a
    // connector.
    // If a connector implements AirbyteTraceMessage emission itself, this code will result in an
    // additional one being emitted.
    // this is fine tho because:
    // "The earliest AirbyteTraceMessage where type=error will be used to populate the FailureReason for
    // the sync."
    // from the spec:
    // https://docs.google.com/document/d/1ctrj3Yh_GjtQ93aND-WH3ocqGxsmxyC3jfiarrF6NY0/edit#
    LOGGER.error(logMessage, e);
    if (STRINGS_TO_REMOVE.isEmpty()) {
      // If there are no strings to deinterpolate, then just emit a naive trace message.
      AirbyteTraceMessageUtility.emitSystemErrorTrace(e, logMessage);
    } else {
      final String mangledMessage = STRINGS_TO_REMOVE.stream().reduce(
          e.getMessage(),
          (message, targetString) -> message.replace(targetString, "?"));
      AirbyteTraceMessageUtility.emitCustomErrorTrace(e.getMessage(), mangledMessage);
    }
    terminate();
  }

  // by doing this in a separate method we can mock it to avoid closing the jvm and therefore test
  // properly
  protected void terminate() {
    System.exit(1);
  }

}
