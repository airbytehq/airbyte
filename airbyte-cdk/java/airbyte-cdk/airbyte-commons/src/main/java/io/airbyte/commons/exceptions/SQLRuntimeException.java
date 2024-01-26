/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.commons.exceptions;

import java.sql.SQLException;

/**
 * Wrapper unchecked exception for {@link SQLException}. This can be used in functional interfaces
 * that do not allow checked exceptions without the generic RuntimeException.
 */
public class SQLRuntimeException extends RuntimeException {

  public SQLRuntimeException(final SQLException cause) {
    super(cause);
  }

}
