/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.server.apis;

import io.airbyte.commons.server.errors.BadObjectSchemaKnownException;
import io.airbyte.commons.server.errors.IdNotFoundKnownException;
import io.airbyte.config.persistence.ConfigNotFoundException;
import io.airbyte.validation.json.JsonValidationException;
import java.io.IOException;
import org.slf4j.LoggerFactory;

public class ApiHelper {

  static <T> T execute(final HandlerCall<T> call) {
    try {
      return call.call();
    } catch (final ConfigNotFoundException e) {
      throw new IdNotFoundKnownException(String.format("Could not find configuration for %s: %s.", e.getType(), e.getConfigId()),
          e.getConfigId(), e);
    } catch (final JsonValidationException e) {
      throw new BadObjectSchemaKnownException(
          String.format("The provided configuration does not fulfill the specification. Errors: %s", e.getMessage()), e);
    } catch (final IOException e) {
      throw new RuntimeException(e);
    } catch (final Exception e) {
      LoggerFactory.getLogger(ApiHelper.class).error("Unexpected Exception", e);
      throw e;
    }
  }

  interface HandlerCall<T> {

    T call() throws ConfigNotFoundException, IOException, JsonValidationException;

  }

}
