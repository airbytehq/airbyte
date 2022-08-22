/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.errors;

import static io.airbyte.integrations.base.errors.utils.ConnectorName.DEFAULT;
import static io.airbyte.integrations.base.errors.utils.ConnectorName.MONGO;

import io.airbyte.integrations.base.errors.messages.DefaultErrorMessage;
import io.airbyte.integrations.base.errors.messages.ErrorMessage;
import io.airbyte.integrations.base.errors.messages.MongoDbErrorMessage;
import io.airbyte.integrations.base.errors.utils.ConnectorName;
import java.util.Map;

public class ErrorMessageFactory {

  private final static Map<ConnectorName, ErrorMessage> MAP = Map.of(
      MONGO, new MongoDbErrorMessage(),
      DEFAULT, new DefaultErrorMessage());

  public static ErrorMessage getErrorMessage(ConnectorName name) {
    if (MAP.containsKey(name)) {
      return MAP.get(name);
    }
    return MAP.get(DEFAULT);
  }

}
