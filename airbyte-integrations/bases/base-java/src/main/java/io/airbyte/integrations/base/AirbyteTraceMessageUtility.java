/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import io.airbyte.protocol.models.AirbyteErrorTraceMessage;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage.FailureType;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import java.util.function.Consumer;
import org.apache.commons.lang3.exception.ExceptionUtils;

public final class AirbyteTraceMessageUtility {

  private AirbyteTraceMessageUtility() {}

  public static void emitSystemErrorTrace(final Throwable e, final String displayMessage) {
    emitErrorTrace(e, displayMessage, FailureType.SYSTEM_ERROR);
  }

  public static void emitConfigErrorTrace(final Throwable e, final String displayMessage) {
    emitErrorTrace(e, displayMessage, FailureType.CONFIG_ERROR);
  }

  public static void emitErrorTrace(final Throwable e, final String displayMessage, final FailureType failureType) {
    emitMessage(makeErrorTraceAirbyteMessage(e, displayMessage, failureType));
  }

  // todo: handle the other types of trace message we'll expect in the future, see
  // io.airbyte.protocol.models.AirbyteTraceMessage
  // & the tech spec:
  // https://docs.google.com/document/d/1ctrj3Yh_GjtQ93aND-WH3ocqGxsmxyC3jfiarrF6NY0/edit#
  // public void emitNotificationTrace() {}
  // public void emitMetricTrace() {}

  private static void emitMessage(AirbyteMessage message) {
    // Not sure why defaultOutputRecordCollector is under Destination specifically,
    // but this matches usage elsewhere in base-java
    Consumer<AirbyteMessage> outputRecordCollector = Destination::defaultOutputRecordCollector;
    outputRecordCollector.accept(message);
  }

  private static AirbyteMessage makeErrorTraceAirbyteMessage(
                                                             final Throwable e,
                                                             final String displayMessage,
                                                             final FailureType failureType) {

    return makeAirbyteMessageFromTraceMessage(
        makeAirbyteTraceMessage(AirbyteTraceMessage.Type.ERROR)
            .withError(new AirbyteErrorTraceMessage()
                .withFailureType(failureType)
                .withMessage(displayMessage)
                .withInternalMessage(e.toString())
                .withStackTrace(ExceptionUtils.getStackTrace(e))));
  }

  private static AirbyteMessage makeAirbyteMessageFromTraceMessage(AirbyteTraceMessage airbyteTraceMessage) {
    return new AirbyteMessage().withType(Type.TRACE).withTrace(airbyteTraceMessage);
  }

  private static AirbyteTraceMessage makeAirbyteTraceMessage(final AirbyteTraceMessage.Type traceMessageType) {
    return new AirbyteTraceMessage().withType(traceMessageType).withEmittedAt((double) System.currentTimeMillis());
  }

}
