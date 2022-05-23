/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance;

import io.airbyte.db.Database;
import java.io.IOException;

public interface DatabaseInstance {

  /**
   * Check is a database has been initialized.
   *
   * @deprecated Will be removed in future versions that separate the initialization from
   *             creation/retrieval of an instance.
   */
  @Deprecated(forRemoval = true)
  boolean isInitialized() throws IOException;

  /**
   * Get a database that has been initialized and is ready to use.
   *
   * @deprecated Will be replaced in future versions that separate the initialization from
   *             creation/retrieval of an instance.
   */
  @Deprecated(forRemoval = true)
  Database getInitialized();

  /**
   * Get an empty database and initialize it.
   *
   * @deprecated Will be replaced in future versions that separate the initialization from
   *             creation/retrieval of an instance.
   */
  @Deprecated(forRemoval = true)
  Database getAndInitialize() throws IOException;

}
