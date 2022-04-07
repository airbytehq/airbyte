/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.controllers;

import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Error;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Custom controller that handles global 404 responses for unknown/unmapped paths.
 */
@Controller(value = "/api/notfound")
public class NotFoundController {

  private static final Logger LOGGER = LoggerFactory.getLogger(NotFoundController.class);

  @Error(status = HttpStatus.NOT_FOUND,
         global = true)
  public HttpResponse notFound(final HttpRequest request) {
    // Would like to send the id along but we don't have access to the http request anymore to fetch it
    // from. TODO: Come back to this with issue #4189
    return HttpResponse.status(HttpStatus.NOT_FOUND)
        .body("Object not found.")
        .contentType(MediaType.APPLICATION_JSON);
  }

}
