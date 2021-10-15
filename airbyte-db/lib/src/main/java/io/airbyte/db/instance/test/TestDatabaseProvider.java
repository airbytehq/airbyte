/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.test;

import io.airbyte.db.Database;
import java.io.IOException;

public interface TestDatabaseProvider {

  Database create(final boolean runMigration) throws IOException;

}
