/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.factory;

import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;

/**
 * Temporary factory class that provides convenience methods for creating a {@link DSLContext}
 * instances. This class will be removed once the project has been converted to leverage an
 * application framework to manage the creation and injection of {@link DSLContext} objects.
 *
 * This class replaces direct calls to {@link io.airbyte.db.Databases}.
 */
public class DSLContextFactory {

  /**
   * Constructs a configured {@link DSLContext} instance using the provided configuration.
   *
   * @param dataSource The {@link DataSource} used to connect to the database.
   * @param dialect The SQL dialect to use with objects created from this context.
   * @return The configured {@link DSLContext}.
   */
  public static DSLContext create(final DataSource dataSource, final SQLDialect dialect) {
    return DSL.using(dataSource, dialect);
  }

}
