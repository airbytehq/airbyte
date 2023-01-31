/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.server.errors.KnownException;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Produces;
import io.micronaut.http.server.exceptions.ExceptionHandler;
import jakarta.inject.Singleton;

@Produces
@Singleton
@Requires(classes = KnownException.class)
public class KnownExceptionHandler implements ExceptionHandler<KnownException, HttpResponse> {

  @Override
  public HttpResponse handle(HttpRequest request, KnownException exception) {
    return HttpResponse.status(HttpStatus.valueOf(exception.getHttpCode()))
        .body(Jsons.serialize(exception.getKnownExceptionInfo()))
        .contentType(MediaType.APPLICATION_JSON_TYPE);
  }

}
