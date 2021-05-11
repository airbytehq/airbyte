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

package io.airbyte.integrations.source.clickhouse;

import io.airbyte.db.jdbc.JdbcStreamingQueryConfiguration;
import java.sql.Connection;
import java.sql.PreparedStatement;

public class ClickHouseJdbcStreamingQueryConfiguration implements JdbcStreamingQueryConfiguration {

  /**
   * The reason accept method for ClickHouse is not setting auto commit to false like other JDBC
   * sources is cause method {@link ru.yandex.clickhouse.ClickHouseConnectionImpl#setAutoCommit} is
   * empty. The reason accept method for ClickHouse is not setting fetch size to 1000 like other JDBC
   * sources is cause method {@link ru.yandex.clickhouse.ClickHouseStatementImpl#setFetchSize} is
   * empty
   */
  @Override
  public void accept(Connection connection, PreparedStatement preparedStatement) {}

}
