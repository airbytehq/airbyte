/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.base.destination.typing_deduping;

public class UnexpectedSchemaException extends RuntimeException {

  public UnexpectedSchemaException(String message) {
    super(message);
  }

}
