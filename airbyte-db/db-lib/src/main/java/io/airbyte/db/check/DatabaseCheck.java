/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.check;

/**
 * Defines the interface for performing checks against a database.
 */
public interface DatabaseCheck {

  /**
   * Checks whether the configured database is available.
   *
   * @throws DatabaseCheckException if unable to perform the check.
   */
  void check() throws DatabaseCheckException;

}
