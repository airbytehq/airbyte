/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.instance.configs;

import io.airbyte.db.Database;
import io.airbyte.db.init.DatabaseInitializationException;
import io.airbyte.db.instance.AbstractDatabaseTest;
import io.airbyte.db.instance.test.TestDatabaseProviders;
import java.io.IOException;
import javax.sql.DataSource;
import org.jooq.DSLContext;

public abstract class AbstractConfigsDatabaseTest extends AbstractDatabaseTest {

  @Override
  public Database getDatabase(final DataSource dataSource, final DSLContext dslContext) throws IOException, DatabaseInitializationException {
    return new TestDatabaseProviders(dataSource, dslContext).turnOffMigration().createNewConfigsDatabase();
  }

}
