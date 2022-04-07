/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

import io.micronaut.context.annotation.Requires;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Produces;
import io.micronaut.http.server.exceptions.ExceptionHandler;
import javax.inject.Singleton;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Produces
@Singleton
@Requires(classes = KnownException.class)
public class KnownExceptionMapper implements ExceptionHandler<KnownException, HttpResponse> {

  private static final Logger LOGGER = LoggerFactory.getLogger(KnownExceptionMapper.class);

  @Override
  public HttpResponse handle(final HttpRequest request, final KnownException exception) {
    return HttpResponse.status(HttpStatus.valueOf(exception.getHttpCode()))
        .body(exception.getKnownExceptionInfo())
        .contentType(MediaType.APPLICATION_JSON_TYPE);
  }

}
