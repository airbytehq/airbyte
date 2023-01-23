/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.errors;

import io.airbyte.commons.json.Jsons;
import io.micronaut.context.annotation.Requires;
import io.micronaut.http.annotation.Produces;
import jakarta.inject.Singleton;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Produces
@Singleton
@Requires(classes = KnownException.class)
public class KnownExceptionMapper implements ExceptionMapper<KnownException> {

  private static final Logger LOGGER = LoggerFactory.getLogger(KnownExceptionMapper.class);

  @Override
  public Response toResponse(final KnownException e) {
    LOGGER.info("Known exception", e.getKnownExceptionInfo());
    return Response.status(e.getHttpCode())
        .entity(Jsons.serialize(e.getKnownExceptionInfo()))
        .type("application/json")
        .build();
  }

}
