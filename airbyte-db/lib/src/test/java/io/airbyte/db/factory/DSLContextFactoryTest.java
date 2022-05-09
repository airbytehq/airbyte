/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db.factory;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;

import javax.sql.DataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.junit.jupiter.api.Test;
import org.postgresql.Driver;

/**
 * Test suite for the {@link DSLContextFactory} class.
 */
public class DSLContextFactoryTest extends AbstractFactoryTest {

  @Test
  void testCreatingADslContext() {
    final DataSource dataSource =
        DataSourceFactory.create(container.getUsername(), container.getPassword(), Driver.class.getName(), container.getJdbcUrl());
    final SQLDialect dialect = SQLDialect.POSTGRES;
    final DSLContext dslContext = DSLContextFactory.create(dataSource, dialect);
    assertNotNull(dslContext);
    assertEquals(dialect, dslContext.configuration().dialect());
  }

}
