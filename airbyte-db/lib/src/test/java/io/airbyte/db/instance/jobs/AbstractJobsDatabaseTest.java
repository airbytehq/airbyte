/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.jobs;

import io.airbyte.db.Database;
import io.airbyte.db.instance.AbstractDatabaseTest;
import java.io.IOException;

public abstract class AbstractJobsDatabaseTest extends AbstractDatabaseTest {

  @Override
  public Database getAndInitializeDatabase(String username, String password, String connectionString) throws IOException {
    return new JobsDatabaseInstance(username, password, connectionString).getAndInitialize();
  }

}
