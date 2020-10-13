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

import java.sql.Connection;
import java.sql.SQLException;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.DSLContext;
import org.jooq.SQLDialect;
import org.jooq.impl.DSL;

public class DatabaseHelper {

  public static BasicDataSource getConnectionPool(String username,
                                                  String password,
                                                  String jdbcConnectionString) {

    BasicDataSource connectionPool = new BasicDataSource();
    connectionPool.setDriverClassName("org.postgresql.Driver");
    connectionPool.setUsername(username);
    connectionPool.setPassword(password);
    connectionPool.setUrl(jdbcConnectionString);

    return connectionPool;
  }

  public static <T> T query(BasicDataSource connectionPool, ContextQueryFunction<T> transform) throws SQLException {

    try (Connection connection = connectionPool.getConnection()) {
      DSLContext context = getContext(connection);
      return transform.apply(context);
    }
  }

  public static <T> T transaction(BasicDataSource connectionPool, ContextQueryFunction<T> transform) throws SQLException {
    try (Connection connection = connectionPool.getConnection()) {
      DSLContext context = getContext(connection);
      return context.transactionResult(configuration -> {
        DSLContext transactionContext = DSL.using(configuration);
        return transform.apply(transactionContext);
      });
    }
  }

  private static DSLContext getContext(Connection connection) {
    return DSL.using(connection, SQLDialect.POSTGRES);
  }

}
