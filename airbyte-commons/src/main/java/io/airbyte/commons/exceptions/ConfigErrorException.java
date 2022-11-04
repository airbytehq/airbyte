/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.exceptions;

/**
 * An exception that indicates that there is something wrong with the user's connector setup. This
 * exception is caught and emits an AirbyteTraceMessage.
 */
public class ConfigErrorException extends RuntimeException {

  private final String displayMessage;

  public ConfigErrorException(final String displayMessage) {
    super(displayMessage);
    this.displayMessage = displayMessage;
  }

  public ConfigErrorException(final String displayMessage, final Throwable exception) {
    super(displayMessage, exception);
    this.displayMessage = displayMessage;
  }

  public String getDisplayMessage() {
    return displayMessage;
  }

}
