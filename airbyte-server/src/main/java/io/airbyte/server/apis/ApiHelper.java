/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import static io.airbyte.metrics.lib.ApmTraceConstants.ENDPOINT_EXECUTION_OPERATION_NAME;

import datadog.trace.api.Trace;
import io.airbyte.commons.server.errors.BadObjectSchemaKnownException;
import io.airbyte.commons.server.errors.IdNotFoundKnownException;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.metrics.lib.ApmTraceUtils;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import org.slf4j.LoggerFactory;

public class ApiHelper {

  @Trace(operationName = ENDPOINT_EXECUTION_OPERATION_NAME)
  static <T> T execute(final HandlerCall<T> call) {
    try {
      return call.call();
    } catch (final ConfigNotFoundException e) {
      ApmTraceUtils.recordErrorOnRootSpan(e);
      throw new IdNotFoundKnownException(String.format("Could not find configuration for %s: %s.", e.getType(), e.getConfigId()),
          e.getConfigId(), e);
    } catch (final JsonValidationException e) {
      ApmTraceUtils.recordErrorOnRootSpan(e);
      throw new BadObjectSchemaKnownException(
          String.format("The provided configuration does not fulfill the specification. Errors: %s", e.getMessage()), e);
    } catch (final IOException e) {
      ApmTraceUtils.recordErrorOnRootSpan(e);
      throw new RuntimeException(e);
    } catch (final Exception e) {
      ApmTraceUtils.recordErrorOnRootSpan(e);
      LoggerFactory.getLogger(ApiHelper.class).error("Unexpected Exception", e);
      throw e;
    }
  }

  interface HandlerCall<T> {

    T call() throws ConfigNotFoundException, IOException, JsonValidationException;

  }

}
