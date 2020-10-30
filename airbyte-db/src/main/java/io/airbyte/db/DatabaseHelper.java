/*
 * MIT License
 *
 * Copyright (c) 2020 Airbyte
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 */

package io.airbyte.db;

import static org.jooq.impl.DSL.currentSchema;

import com.google.common.collect.Sets;
import io.airbyte.commons.json.Jsons;
import java.io.Serializable;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.Record1;
import org.jooq.Result;
import org.jooq.SQLDialect;
import org.jooq.Table;
import org.jooq.impl.DSL;
import org.jooq.impl.SchemaImpl;

public class DatabaseHelper {

  // default to postgres (which is the driver that is installed with this library).
  public static BasicDataSource getConnectionPool(String username, String password, String jdbcConnectionString) {

    return getConnectionPool(username, password, jdbcConnectionString, "org.postgresql.Driver");
  }

  public static BasicDataSource getConnectionPool( String username,String password,String jdbcConnectionString, String driverClassName) {
    final BasicDataSource connectionPool = new BasicDataSource();
    connectionPool.setDriverClassName(driverClassName);
    connectionPool.setUsername(username);
    connectionPool.setPassword(password);
    connectionPool.setUrl(jdbcConnectionString);

    return connectionPool;
  }

  // default to postgres dialect
  public static <T> T query(BasicDataSource connectionPool, ContextQueryFunction<T> transform) throws SQLException {
    return query(connectionPool, transform, SQLDialect.POSTGRES);
  }
  public static <T> T query(BasicDataSource connectionPool, ContextQueryFunction<T> transform, SQLDialect dialect) throws SQLException {
    try (final Connection connection = connectionPool.getConnection()) {
      DSLContext context = getContext(connection, dialect);
      return transform.apply(context);
    }
  }

  public static <T> T transaction(BasicDataSource connectionPool, ContextQueryFunction<T> transform) throws SQLException {
    try (final Connection connection = connectionPool.getConnection()) {
      DSLContext context = getContext(connection, SQLDialect.POSTGRES);
      return context.transactionResult(configuration -> {
        DSLContext transactionContext = DSL.using(configuration);
        return transform.apply(transactionContext);
      });
    }
  }

  public static DSLContext getContext(Connection connection, SQLDialect dialect) {
    return DSL.using(connection, dialect);
  }
}
