/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors.messages;

import java.util.Objects;

public class ErrorMessage {

  // TODO: this could be built using a Builder design pattern instead of passing in 0 to indicate no
  // errorCode exists
  public static String getErrorMessage(final String stateCode, final int errorCode, final String message, final Exception exception) {
    if (Objects.isNull(message)) {
      return configMessage(stateCode, 0, exception.getMessage());
    } else {
      return configMessage(stateCode, errorCode, message);
    }
  }

  private static String configMessage(final String stateCode, final int errorCode, final String message) {
    final String stateCodePart = Objects.isNull(stateCode) ? "" : String.format("State code: %s; ", stateCode);
    final String errorCodePart = errorCode == 0 ? "" : String.format("Error code: %s; ", errorCode);
    return String.format("%s%sMessage: %s", stateCodePart, errorCodePart, message);
  }

}
