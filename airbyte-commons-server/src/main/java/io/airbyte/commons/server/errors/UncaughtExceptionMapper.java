/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.server.errors;

import io.airbyte.api.model.generated.KnownExceptionInfo;
import io.airbyte.commons.json.Jsons;
import javax.ws.rs.core.Response;
import javax.ws.rs.ext.ExceptionMapper;
import javax.ws.rs.ext.Provider;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Provider
public class UncaughtExceptionMapper implements ExceptionMapper<Throwable> {

  private static final Logger LOGGER = LoggerFactory.getLogger(UncaughtExceptionMapper.class);

  @Override
  public Response toResponse(final Throwable e) {
    LOGGER.error("Uncaught exception", e);
    final KnownExceptionInfo exceptionInfo = KnownException.infoFromThrowableWithMessage(e, "Internal Server Error: " + e.getMessage());
    return Response.status(500)
        .entity(Jsons.serialize(exceptionInfo))
        .type("application/json")
        .build();
  }

}
