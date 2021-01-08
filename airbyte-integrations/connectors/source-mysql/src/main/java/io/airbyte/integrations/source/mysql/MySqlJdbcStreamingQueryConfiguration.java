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

package io.airbyte.integrations.source.mysql;

import io.airbyte.db.jdbc.JdbcStreamingQueryConfiguration;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class MySqlJdbcStreamingQueryConfiguration implements JdbcStreamingQueryConfiguration {

  @Override
  public void accept(Connection connection, PreparedStatement preparedStatement) throws SQLException {
    // This is only respected if "useCursorFetch=true" is set in the connection. See the "resultset"
    // section the MySql docs for more details.
    // https://dev.mysql.com/doc/connector-j/8.0/en/connector-j-reference-implementation-notes.html.
    // When using this approach MySql creates a temporary table which may have some effect on db
    // performance.
    // e.g. conn = DriverManager.getConnection("jdbc:mysql://localhost/?useCursorFetch=true", "user",
    // "s3cr3t");
    // We set userCursorFetch in MySqlSource.
    connection.setAutoCommit(false);
    preparedStatement.setFetchSize(1000);
    // If for some reason, you cannot set useCursorFetch in the connection, fall back on this
    // implementation below. It fetches records one at a time, which while inefficient, at least does
    // not risk OOM.
    // connection.setAutoCommit(false);
    // preparedStatement.setFetchSize(Integer.MIN_VALUE);
  }

}
