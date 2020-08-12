package io.dataline.server.errors;

import com.fasterxml.jackson.databind.ObjectMapper;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;

@Provider
public class KnownExceptionMapper implements ExceptionMapper<KnownException> {

  @Override
  public Response toResponse(KnownException e) {
    return Response.status(e.getHttpCode())
        .entity(new ObjectMapper().createObjectNode().put("message: ", e.getMessage()))
        .type("application/json")
        .build();
  }
}
