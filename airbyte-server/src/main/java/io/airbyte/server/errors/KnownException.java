/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

import io.airbyte.api.model.KnownExceptionInfo;
import org.apache.logging.log4j.core.util.Throwables;

public abstract class KnownException extends RuntimeException {

  public KnownException(String message) {
    super(message);
  }

  public KnownException(String message, Throwable cause) {
    super(message, cause);
  }

  abstract public int getHttpCode();

  public KnownExceptionInfo getKnownExceptionInfo() {
    return KnownException.infoFromThrowable(this);
  }

  public static KnownExceptionInfo infoFromThrowableWithMessage(Throwable t, String message) {
    KnownExceptionInfo exceptionInfo = new KnownExceptionInfo()
        .exceptionClassName(t.getClass().getName())
        .message(message)
        .exceptionStack(Throwables.toStringList(t));
    if (t.getCause() != null) {
      exceptionInfo.rootCauseExceptionClassName(t.getClass().getClass().getName());
      exceptionInfo.rootCauseExceptionStack(Throwables.toStringList(t.getCause()));
    }
    return exceptionInfo;
  }

  public static KnownExceptionInfo infoFromThrowable(Throwable t) {
    return infoFromThrowableWithMessage(t, t.getMessage());
  }

}
