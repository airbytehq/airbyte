/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class AirbyteExceptionHandler implements Thread.UncaughtExceptionHandler {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteExceptionHandler.class);
  public static final String logMessage = "Something went wrong in the connector. See the logs for more details.";

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
    AirbyteTraceMessageUtility.emitSystemErrorTrace(e, logMessage);
    terminate();
  }

  // by doing this in a separate method we can mock it to avoid closing the jvm and therefore test
  // properly
  protected void terminate() {
    System.exit(1);
  }

}
