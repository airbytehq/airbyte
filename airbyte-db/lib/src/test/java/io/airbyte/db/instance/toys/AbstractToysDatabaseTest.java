/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.toys;

import io.airbyte.db.Database;
import io.airbyte.db.instance.AbstractDatabaseTest;
import java.io.IOException;

public abstract class AbstractToysDatabaseTest extends AbstractDatabaseTest {

  public Database getAndInitializeDatabase(String username, String password, String connectionString) throws IOException {
    return new ToysDatabaseInstance(container.getUsername(), container.getPassword(), container.getJdbcUrl()).getAndInitialize();
  }

}
