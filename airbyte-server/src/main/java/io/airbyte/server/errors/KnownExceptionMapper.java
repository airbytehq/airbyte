/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

import io.airbyte.commons.json.Jsons;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Provider
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
