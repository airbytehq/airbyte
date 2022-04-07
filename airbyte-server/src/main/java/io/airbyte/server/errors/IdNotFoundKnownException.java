/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

import io.airbyte.api.model.NotFoundKnownExceptionInfo;
import io.micronaut.http.HttpStatus;
import org.apache.logging.log4j.core.util.Throwables;

public class IdNotFoundKnownException extends KnownException {

  String id;

  public IdNotFoundKnownException(final String message, final String id) {
    super(message);
    this.id = id;
  }

  public IdNotFoundKnownException(final String message, final String id, final Throwable cause) {
    super(message, cause);
    this.id = id;
  }

  public IdNotFoundKnownException(final String message, final Throwable cause) {
    super(message, cause);
  }

  @Override
  public int getHttpCode() {
    return HttpStatus.NOT_FOUND.getCode();
  }

  public String getId() {
    return id;
  }

  public NotFoundKnownExceptionInfo getNotFoundKnownExceptionInfo() {
    final NotFoundKnownExceptionInfo exceptionInfo = new NotFoundKnownExceptionInfo()
        .exceptionClassName(this.getClass().getName())
        .exceptionStack(Throwables.toStringList(this))
        .message(this.getMessage());
    if (this.getCause() != null) {
      exceptionInfo.rootCauseExceptionClassName(this.getClass().getClass().getName());
      exceptionInfo.rootCauseExceptionStack(Throwables.toStringList(this.getCause()));
    }
    exceptionInfo.id(this.getId());
    return exceptionInfo;
  }

}
