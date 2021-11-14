/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.jdbc;

import com.fasterxml.jackson.databind.JsonNode;
import com.google.common.collect.ImmutableList;
import com.google.common.collect.ImmutableMap;
import io.airbyte.commons.functional.CheckedConsumer;
import io.airbyte.commons.json.Jsons;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.Databases;
import io.airbyte.db.SqlDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcSourceOperations;
import io.airbyte.db.jdbc.JdbcStreamingQueryConfiguration;
import io.airbyte.db.jdbc.JdbcUtils;
import io.airbyte.integrations.base.Source;
import io.airbyte.integrations.source.relationaldb.AbstractRelationalDbSource;
import io.airbyte.integrations.source.relationaldb.TableInfo;
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.JsonSchemaPrimitive;
import java.sql.JDBCType;
import java.sql.PreparedStatement;
import java.sql.SQLException;
import java.util.AbstractMap.SimpleImmutableEntry;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.apache.commons.lang3.tuple.ImmutablePair;
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

  @Override
  public JDBCType getFieldType(final JsonNode field) {
    JDBCType jdbcType;
    try {
      return JDBCType.valueOf(field.get(INTERNAL_COLUMN_TYPE).asInt());
    } catch (final IllegalArgumentException ex) {
      LOGGER.warn(String.format("Could not convert column: %s from table: %s.%s with type: %s. Casting to VARCHAR.",
          field.get(INTERNAL_COLUMN_NAME),
          field.get(INTERNAL_SCHEMA_NAME),
          field.get(INTERNAL_TABLE_NAME),
          field.get(INTERNAL_COLUMN_TYPE)));
      return JDBCType.VARCHAR;
    }
  }

}
