package io.dataline.server.errors;

import com.fasterxml.jackson.databind.ObjectMapper;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;

@Provider
public class CatchAllExceptionMapper implements ExceptionMapper<Throwable> {

  @Override
  public Response toResponse(Throwable e) {
    return Response.status(500)
        .entity(
            new ObjectMapper()
                .createObjectNode()
                .put("message", "internal server error")
                .toString())
        .type("application/json")
        .build();
  }
}
