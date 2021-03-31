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

import io.airbyte.db.jdbc.DefaultJdbcDatabase;
import io.airbyte.db.jdbc.JdbcDatabase;
import io.airbyte.db.jdbc.JdbcStreamingQueryConfiguration;
import io.airbyte.db.jdbc.StreamingJdbcDatabase;
import org.apache.commons.dbcp2.BasicDataSource;
import org.jooq.SQLDialect;

public class Databases {

  public static Database createPostgresDatabase(String username, String password, String jdbcConnectionString) {
    return createDatabase(username, password, jdbcConnectionString, "org.postgresql.Driver", SQLDialect.POSTGRES);
  }

  public static JdbcDatabase createRedshiftDatabase(String username, String password, String jdbcConnectionString) {
    return createJdbcDatabase(username, password, jdbcConnectionString, "com.amazon.redshift.jdbc.Driver");
  }

  public static Database createDatabase(final String username,
                                        final String password,
                                        final String jdbcConnectionString,
                                        final String driverClassName,
                                        final SQLDialect dialect) {
    final BasicDataSource connectionPool = createBasicDataSource(username, password, jdbcConnectionString, driverClassName);

    return new Database(connectionPool, dialect);
  }

  public static JdbcDatabase createJdbcDatabase(final String username,
                                                final String password,
                                                final String jdbcConnectionString,
                                                final String driverClassName) {
    final BasicDataSource connectionPool = createBasicDataSource(username, password, jdbcConnectionString, driverClassName);

    return new DefaultJdbcDatabase(connectionPool);
  }

  public static JdbcDatabase createStreamingJdbcDatabase(final String username,
                                                         final String password,
                                                         final String jdbcConnectionString,
                                                         final String driverClassName,
                                                         final JdbcStreamingQueryConfiguration jdbcStreamingQuery) {
    final BasicDataSource connectionPool = createBasicDataSource(username, password, jdbcConnectionString, driverClassName);

    final JdbcDatabase defaultJdbcDatabase = createJdbcDatabase(username, password, jdbcConnectionString, driverClassName);
    return new StreamingJdbcDatabase(connectionPool, defaultJdbcDatabase, jdbcStreamingQuery);
  }

  private static BasicDataSource createBasicDataSource(final String username,
                                                       final String password,
                                                       final String jdbcConnectionString,
                                                       final String driverClassName) {
    final BasicDataSource connectionPool = new BasicDataSource();
    connectionPool.setDriverClassName(driverClassName);
    connectionPool.setUsername(username);
    connectionPool.setPassword(password);
    connectionPool.setUrl(jdbcConnectionString);
    return connectionPool;
  }

}
