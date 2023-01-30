/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.micronaut.context.annotation.Requires;
import io.micronaut.http.HttpRequest;
import io.micronaut.http.HttpResponse;
import io.micronaut.http.HttpStatus;
import io.micronaut.http.MediaType;
import io.micronaut.http.annotation.Controller;
import io.micronaut.http.annotation.Error;
import io.micronaut.security.annotation.Secured;
import io.micronaut.security.rules.SecurityRule;

/**
 * Custom controller that handles global 404 responses for unknown/unmapped paths.
 */
@Controller("/api/notfound")
@Requires(property = "airbyte.deployment-mode",
          value = "OSS")
@Secured(SecurityRule.IS_ANONYMOUS)
public class NotFoundController {

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
