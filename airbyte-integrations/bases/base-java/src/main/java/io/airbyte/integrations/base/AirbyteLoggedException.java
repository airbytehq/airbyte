/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base;

import io.airbyte.protocol.models.AirbyteErrorTraceMessage;
import io.airbyte.protocol.models.AirbyteErrorTraceMessage.FailureType;
import io.airbyte.protocol.models.AirbyteMessage;
import io.airbyte.protocol.models.AirbyteMessage.Type;
import io.airbyte.protocol.models.AirbyteTraceMessage;
import java.util.Arrays;
import java.util.function.Consumer;

public class AirbyteLoggedException extends Exception {

  private final Throwable e;
  private final String displayMessage;
  private final FailureType failureType;

  public AirbyteLoggedException(final Throwable e, final String displayMessage, final FailureType failureType) {
    this.e = e;
    this.displayMessage = displayMessage;
    this.failureType = failureType;

    // Not sure why defaultOutputRecordCollector is under Destination specifically,
    // but this matches IntegrationRunner usage
    Consumer<AirbyteMessage> outputRecordCollector = Destination::defaultOutputRecordCollector;
    outputRecordCollector.accept(new AirbyteMessage().withType(Type.TRACE).withTrace(makeAirbyteTraceMessage()));
  }

  public AirbyteLoggedException(final Throwable e, final String displayMessage) {
    this(e, displayMessage, FailureType.SYSTEM_ERROR);
  }

  private AirbyteTraceMessage makeAirbyteTraceMessage() {
    AirbyteErrorTraceMessage errorTraceMsg = new AirbyteErrorTraceMessage()
        .withFailureType(this.failureType)
        .withMessage(this.displayMessage)
        .withInternalMessage(this.e.toString())
        .withStackTrace(Arrays.toString(this.e.getStackTrace()));
    return new AirbyteTraceMessage()
        .withType(AirbyteTraceMessage.Type.ERROR)
        .withError(errorTraceMsg)
        .withEmittedAt((double) System.currentTimeMillis());
  }
}
