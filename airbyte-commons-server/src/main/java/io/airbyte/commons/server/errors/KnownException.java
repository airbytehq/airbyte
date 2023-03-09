/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.errors;

import io.airbyte.api.model.generated.KnownExceptionInfo;
import org.apache.logging.log4j.core.util.Throwables;

public abstract class KnownException extends RuntimeException {

  public KnownException(final String message) {
    super(message);
  }

  public KnownException(final String message, final Throwable cause) {
    super(message, cause);
  }

  abstract public int getHttpCode();

  public KnownExceptionInfo getKnownExceptionInfo() {
    return KnownException.infoFromThrowable(this);
  }

  public static KnownExceptionInfo infoFromThrowableWithMessage(final Throwable t, final String message) {
    final KnownExceptionInfo exceptionInfo = new KnownExceptionInfo()
        .exceptionClassName(t.getClass().getName())
        .message(message)
        .exceptionStack(Throwables.toStringList(t));
    if (t.getCause() != null) {
      exceptionInfo.rootCauseExceptionClassName(t.getClass().getClass().getName());
      exceptionInfo.rootCauseExceptionStack(Throwables.toStringList(t.getCause()));
    }
    return exceptionInfo;
  }

  public static KnownExceptionInfo infoFromThrowable(final Throwable t) {
    return infoFromThrowableWithMessage(t, t.getMessage());
  }

}
