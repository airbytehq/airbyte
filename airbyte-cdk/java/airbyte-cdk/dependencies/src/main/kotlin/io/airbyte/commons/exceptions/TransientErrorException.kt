package io.airbyte.commons.exceptions;

/**
 * An exception that indicates a transient error was encountered. This
 * exception is caught and emits an AirbyteTraceMessage.
 */
class TransientErrorException : RuntimeException {
  val displayMessage: String

  constructor(displayMessage: String) : super(displayMessage) {
    this.displayMessage = displayMessage
  }

  constructor(displayMessage: String, exception: Throwable?) : super(displayMessage, exception) {
    this.displayMessage = displayMessage
  }
}
