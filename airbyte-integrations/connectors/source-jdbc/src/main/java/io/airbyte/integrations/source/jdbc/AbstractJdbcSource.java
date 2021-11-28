/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.jdbc;

import io.airbyte.db.jdbc.JdbcSourceOperations;
import io.airbyte.db.jdbc.JdbcStreamingQueryConfiguration;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Source;
import java.sql.JDBCType;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class contains helper functions and boilerplate for implementing a source connector for a
 * relational DB source which can be accessed via JDBC driver. If you are implementing a connector
 * for a relational DB which has a JDBC driver, make an effort to use this class.
 */
public abstract class AbstractJdbcSource extends AbstractJdbcCompatibleSource<JDBCType> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractJdbcSource.class);

  public AbstractJdbcSource(final String driverClass, final JdbcStreamingQueryConfiguration jdbcStreamingQueryConfiguration) {
    this(driverClass, jdbcStreamingQueryConfiguration, JdbcUtils.getDefaultSourceOperations());
  }

  public AbstractJdbcSource(final String driverClass,
                            final JdbcStreamingQueryConfiguration jdbcStreamingQueryConfiguration,
                            final JdbcSourceOperations sourceOperations) {
    super(driverClass, jdbcStreamingQueryConfiguration, sourceOperations);
  }

}
