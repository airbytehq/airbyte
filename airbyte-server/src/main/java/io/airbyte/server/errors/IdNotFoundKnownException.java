/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

import io.airbyte.api.model.NotFoundKnownExceptionInfo;
import org.apache.logging.log4j.core.util.Throwables;

public class IdNotFoundKnownException extends KnownException {

  String id;

  public IdNotFoundKnownException(String message, String id) {
    super(message);
    this.id = id;
  }

  public IdNotFoundKnownException(String message, String id, Throwable cause) {
    super(message, cause);
    this.id = id;
  }

  public IdNotFoundKnownException(String message, Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return 404;
  }

  public String getId() {
    return id;
  }

  public NotFoundKnownExceptionInfo getNotFoundKnownExceptionInfo() {
    NotFoundKnownExceptionInfo exceptionInfo = new NotFoundKnownExceptionInfo()
        .exceptionClassName(this.getClass().getName())
        .message(this.getMessage())
        .exceptionStack(Throwables.toStringList(this));
    if (this.getCause() != null) {
      exceptionInfo.rootCauseExceptionClassName(this.getClass().getClass().getName());
      exceptionInfo.rootCauseExceptionStack(Throwables.toStringList(this.getCause()));
    }
    exceptionInfo.id(this.getId());
    return exceptionInfo;
  }

}
