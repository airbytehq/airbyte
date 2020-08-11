package io.dataline.server.errors;

import com.fasterxml.jackson.databind.JsonMappingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;

@Provider
public class InvalidInputExceptionMapper implements ExceptionMapper<JsonMappingException> {
  @Override
  public Response toResponse(JsonMappingException e) {
    return Response.status(422)
        .entity(
            new ObjectMapper()
                .createObjectNode()
                .put("message", "The received object did not pass validation")
                .put("details", e.getOriginalMessage())
                .toString())
        .type("application/json")
        .build();
  }
}
