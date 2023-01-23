/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.errors;

import com.fasterxml.jackson.databind.JsonMappingException;
import io.airbyte.commons.json.Jsons;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;

@Provider
public class InvalidJsonInputExceptionMapper implements ExceptionMapper<JsonMappingException> {

  @Override
  public Response toResponse(final JsonMappingException e) {
    return Response.status(422)
        .entity(
            Jsons.serialize(KnownException.infoFromThrowableWithMessage(e, "Invalid json input. " + e.getMessage() + " " + e.getOriginalMessage())))
        .type("application/json")
        .build();
  }

}
