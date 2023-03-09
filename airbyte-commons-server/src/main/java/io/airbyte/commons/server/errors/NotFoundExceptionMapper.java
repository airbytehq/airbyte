/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.errors;

import io.airbyte.commons.json.Jsons;
import javax.ws.rs.NotFoundException;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Provider
public class NotFoundExceptionMapper implements ExceptionMapper<NotFoundException> {

  private static final Logger LOGGER = LoggerFactory.getLogger(NotFoundExceptionMapper.class);

  @Override
  public Response toResponse(final NotFoundException e) {
    // Would like to send the id along but we don't have access to the http request anymore to fetch it
    // from. TODO: Come back to this with issue #4189
    final IdNotFoundKnownException idnf = new IdNotFoundKnownException("Object not found. " + e.getMessage(), e);
    LOGGER.error("Not found exception", idnf.getNotFoundKnownExceptionInfo());
    return Response.status(404)
        .entity(Jsons.serialize(idnf.getNotFoundKnownExceptionInfo()))
        .type("application/json")
        .build();
  }

}
