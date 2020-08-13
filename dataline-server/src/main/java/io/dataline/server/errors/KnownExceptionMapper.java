package io.dataline.server.errors;

import com.fasterxml.jackson.databind.ObjectMapper;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Provider
public class KnownExceptionMapper implements ExceptionMapper<KnownException> {
  private static final Logger LOGGER = LoggerFactory.getLogger(KnownExceptionMapper.class);

  @Override
  public Response toResponse(KnownException e) {
    LOGGER.debug("known exception", e);
    return Response.status(e.getHttpCode())
        .entity(new ObjectMapper().createObjectNode().put("message", e.getMessage()))
        .type("application/json")
        .build();
  }
}
