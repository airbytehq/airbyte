/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.errors;

import io.micronaut.context.annotation.Requires;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Produces;
import io.micronaut.http.server.exceptions.ExceptionHandler;
import jakarta.inject.Singleton;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Produces
@Singleton
@Requires(classes = IdNotFoundKnownException.class)
public class IdNotFoundExceptionMapper implements ExceptionHandler<IdNotFoundKnownException, HttpResponse> {

  private static final Logger LOGGER = LoggerFactory.getLogger(IdNotFoundExceptionMapper.class);

  @Override
  public HttpResponse handle(final HttpRequest request, final IdNotFoundKnownException exception) {
    final IdNotFoundKnownException idnf = new IdNotFoundKnownException("Id not found: " + exception.getMessage(), exception);
    LOGGER.error("Not found exception", idnf.getNotFoundKnownExceptionInfo());

    return HttpResponse.status(HttpStatus.NOT_FOUND)
        .body(KnownException.infoFromThrowableWithMessage(exception, "Internal Server Error: " + exception.getMessage()))
        .contentType(MediaType.APPLICATION_JSON);
  }

}
