package io.dataline.server.errors;

import com.fasterxml.jackson.core.JsonParseException;
import com.fasterxml.jackson.databind.ObjectMapper;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;

@Provider
public class InvalidJsonExceptionMapper implements ExceptionMapper<JsonParseException> {
  @Override
  public Response toResponse(JsonParseException e) {
    return Response.status(422)
        .entity(
            new ObjectMapper()
                .createObjectNode()
                .put("message", "Invalid JSON")
                .put("details", e.getOriginalMessage()))
        .type("application/json")
        .build();
  }
}
