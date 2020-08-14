package io.dataline.server.errors;

import com.fasterxml.jackson.databind.ObjectMapper;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Provider
public class CatchAllExceptionMapper implements ExceptionMapper<Throwable> {
  private static final Logger LOGGER = LoggerFactory.getLogger(CatchAllExceptionMapper.class);

  @Override
  public Response toResponse(Throwable e) {
    LOGGER.debug("catch all exception", e);
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
