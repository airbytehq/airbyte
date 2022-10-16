/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.check;

/**
 * Custom exception that represents a failure that occurs during an attempt to check the
 * availability or migration status of a database.
 */
public class DatabaseCheckException extends Exception {

  public DatabaseCheckException(final String message) {
    super(message);
  }

  public DatabaseCheckException(final String message, final Throwable cause) {
    super(message, cause);
  }

}
