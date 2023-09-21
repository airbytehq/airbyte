/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.stream.AirbyteStreamStatusHolder;
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage;
import io.airbyte.protocol.models.v0.AirbyteErrorTraceMessage.FailureType;
import io.airbyte.protocol.models.v0.AirbyteEstimateTraceMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage;
import io.airbyte.protocol.models.v0.AirbyteMessage.Type;
import io.airbyte.protocol.models.v0.AirbyteTraceMessage;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public final class AirbyteTraceMessageUtility {

  private static final Logger LOGGER = LoggerFactory.getLogger(AirbyteTraceMessageUtility.class);

  private AirbyteTraceMessageUtility() {}

  public static void emitSystemErrorTrace(final Throwable e, final String displayMessage) {
    LOGGER.info("Emitting error trace...");
    emitErrorTrace(e, displayMessage, FailureType.SYSTEM_ERROR);
  }

  public static void emitConfigErrorTrace(final Throwable e, final String displayMessage) {
    emitErrorTrace(e, displayMessage, FailureType.CONFIG_ERROR);
  }

  public static void emitEstimateTrace(final long byteEstimate,
                                       final AirbyteEstimateTraceMessage.Type type,
                                       final long rowEstimate,
                                       final String streamName,
                                       final String streamNamespace) {
    emitMessage(makeAirbyteMessageFromTraceMessage(
        makeAirbyteTraceMessage(AirbyteTraceMessage.Type.ESTIMATE)
            .withEstimate(new AirbyteEstimateTraceMessage()
                .withByteEstimate(byteEstimate)
                .withType(type)
                .withRowEstimate(rowEstimate)
                .withName(streamName)
                .withNamespace(streamNamespace))));
  }

  public static void emitErrorTrace(final Throwable e, final String displayMessage, final FailureType failureType) {
    emitMessage(makeErrorTraceAirbyteMessage(e, displayMessage, failureType));
  }

  public static void emitStreamStatusTrace(final AirbyteStreamStatusHolder airbyteStreamStatusHolder) {
    emitMessage(makeStreamStatusTraceAirbyteMessage(airbyteStreamStatusHolder));
  }

  // todo: handle the other types of trace message we'll expect in the future, see
  // io.airbyte.protocol.models.v0.AirbyteTraceMessage
  // & the tech spec:
  // https://docs.google.com/document/d/1ctrj3Yh_GjtQ93aND-WH3ocqGxsmxyC3jfiarrF6NY0/edit#
  // public void emitNotificationTrace() {}
  // public void emitMetricTrace() {}

  private static void emitMessage(final AirbyteMessage message) {
    // Explicitly use System.out.println here instead of the OutputRecordConsumer
    // This is to avoid having multiple PrintWriter instances pointing at the standard out file
    // descriptor
    System.out.println(Jsons.serialize(message));
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

  private static AirbyteMessage makeStreamStatusTraceAirbyteMessage(final AirbyteStreamStatusHolder airbyteStreamStatusHolder) {
    return makeAirbyteMessageFromTraceMessage(airbyteStreamStatusHolder.toTraceMessage());
  }

  private static AirbyteMessage makeAirbyteMessageFromTraceMessage(final AirbyteTraceMessage airbyteTraceMessage) {
    return new AirbyteMessage().withType(Type.TRACE).withTrace(airbyteTraceMessage);
  }

  private static AirbyteTraceMessage makeAirbyteTraceMessage(final AirbyteTraceMessage.Type traceMessageType) {
    return new AirbyteTraceMessage().withType(traceMessageType).withEmittedAt((double) System.currentTimeMillis());
  }

}
