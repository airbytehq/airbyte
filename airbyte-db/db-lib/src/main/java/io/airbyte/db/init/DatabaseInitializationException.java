/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.init;

/**
 * Custom exception that represents a failure that occurs during an attempt to initialize a
 * database.
 */
public class DatabaseInitializationException extends Exception {

  public DatabaseInitializationException(final String message) {
    super(message);
  }

  public DatabaseInitializationException(final String message, final Throwable cause) {
    super(message, cause);
  }

}
