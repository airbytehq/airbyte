/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import java.util.Objects;

public class ErrorMessage {

  private static final String DEFAULT_ERROR_MESSAGE = "State code: %s. Error Message: %s.";

  public static String getDefaultErrorMessage(String errorCode, Exception exception) {
    return String.format(DEFAULT_ERROR_MESSAGE, errorCode, exception.getMessage());
  }

  public static String getErrorMessage(String stateCode, int errorCode, String message, Exception exception) {
    if (Objects.isNull(message)) {
      return getDefaultErrorMessage(stateCode, exception);
    } else {
      return configMessage(stateCode, errorCode, message);
    }
  }

  private static String configMessage(String stateCode, int errorCode, String message) {
    var stateCodePart = Objects.isNull(stateCode) ? "" : "State code: " + stateCode + "; ";
    var errorCodePart = errorCode == 0 ? "" : "Error code: " + errorCode + "; ";
    return stateCodePart + errorCodePart + "Message: " + message;
  }

}
