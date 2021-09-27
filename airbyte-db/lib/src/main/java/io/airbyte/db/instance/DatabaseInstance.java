/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

import io.airbyte.db.Database;
import java.io.IOException;

public interface DatabaseInstance {

  /**
   * Check is a database has been initialized.
   */
  boolean isInitialized() throws IOException;

  /**
   * Get a database that has been initialized and is ready to use.
   */
  Database getInitialized();

  /**
   * Get an empty database and initialize it.
   */
  Database getAndInitialize() throws IOException;

}
