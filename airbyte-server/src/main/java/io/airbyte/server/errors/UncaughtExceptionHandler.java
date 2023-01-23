/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

import io.airbyte.commons.server.errors.KnownException;
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
@Requires(classes = Throwable.class)
public class UncaughtExceptionHandler implements ExceptionHandler<Throwable, HttpResponse> {

  private static final Logger LOGGER = LoggerFactory.getLogger(UncaughtExceptionHandler.class);

  @Override
  public HttpResponse handle(final HttpRequest request, final Throwable exception) {
    LOGGER.error("Uncaught exception", exception);
    return HttpResponse.status(HttpStatus.INTERNAL_SERVER_ERROR)
        .body(KnownException.infoFromThrowableWithMessage(exception, "Internal Server Error: " + exception.getMessage()))
        .contentType(MediaType.APPLICATION_JSON);
  }

}
