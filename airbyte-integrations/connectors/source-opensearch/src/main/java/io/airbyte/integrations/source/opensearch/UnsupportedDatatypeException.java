/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.opensearch;

public class UnsupportedDatatypeException extends Exception {

  public UnsupportedDatatypeException(String message) {
    super(message);
  }

}
