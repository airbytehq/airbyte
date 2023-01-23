/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.errors;

import io.airbyte.commons.json.Jsons;
import javax.validation.ConstraintViolationException;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;

@Provider
public class InvalidInputExceptionMapper implements ExceptionMapper<ConstraintViolationException> {

  @Override
  public Response toResponse(final ConstraintViolationException e) {
    return Response.status(Response.Status.BAD_REQUEST)
        .entity(Jsons.serialize(InvalidInputExceptionHandler.infoFromConstraints(e)))
        .type("application/json")
        .build();
  }

}
