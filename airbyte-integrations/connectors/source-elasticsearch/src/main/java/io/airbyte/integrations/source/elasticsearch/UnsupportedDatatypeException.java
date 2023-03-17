/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.elasticsearch;

public class UnsupportedDatatypeException extends Exception {

  public UnsupportedDatatypeException(String message) {
    super(message);
  }

}
