/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import java.util.Objects;

public class ErrorMessage {

  public static String getDefaultErrorMessage(String stateCode, Exception exception) {
    return configMessage(stateCode, 0, exception.getLocalizedMessage());
  }

  public static String getErrorMessage(String stateCode, int errorCode, String message, Exception exception) {
    if (Objects.isNull(message)) {
      return getDefaultErrorMessage(stateCode, exception);
    } else {
      return configMessage(stateCode, errorCode, message);
    }
  }

  private static String configMessage(String stateCode, int errorCode, String message) {
    String stateCodePart = Objects.isNull(stateCode) ? "" : String.format("State code: %s; ", stateCode);
    String errorCodePart = errorCode == 0 ? "" : String.format("Error code: %s; ", errorCode);
    return String.format("%s%sMessage: %s", stateCodePart, errorCodePart, message);
  }

}
