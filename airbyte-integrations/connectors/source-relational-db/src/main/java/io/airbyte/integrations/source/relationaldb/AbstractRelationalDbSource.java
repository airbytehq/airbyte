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

package io.airbyte.integrations.source.relationaldb;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.util.AutoCloseableIterator;
import io.airbyte.commons.util.AutoCloseableIterators;
import io.airbyte.db.SqlDatabase;
import io.airbyte.integrations.base.Source;
import java.util.List;
import java.util.StringJoiner;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * This class contains helper functions and boilerplate for implementing a source connector for a
 * relational DB source.
 *
 * @see io.airbyte.integrations.source.jdbc.AbstractJdbcSource if you are implementing a relational
 *      DB which can be accessed via JDBC driver.
 */
public abstract class AbstractRelationalDbSource<DataType, Database extends SqlDatabase> extends
    AbstractDbSource<DataType, Database> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractRelationalDbSource.class);

  @Override
  public AutoCloseableIterator<JsonNode> queryTableFullRefresh(final Database database,
                                                               final List<String> columnNames,
                                                               final String schemaName,
                                                               final String tableName) {
    LOGGER.info("Queueing query for table: {}", tableName);
    return queryTable(database, String.format("SELECT %s FROM %s",
        enquoteIdentifierList(columnNames),
        getFullTableName(schemaName, tableName)));
  }

  protected String getIdentifierWithQuoting(final String identifier) {
    return getQuoteString() + identifier + getQuoteString();
  }

  protected String enquoteIdentifierList(final List<String> identifiers) {
    final StringJoiner joiner = new StringJoiner(",");
    for (final String identifier : identifiers) {
      joiner.add(getIdentifierWithQuoting(identifier));
    }
    return joiner.toString();
  }

  protected String getFullTableName(final String nameSpace, final String tableName) {
    return (nameSpace == null || nameSpace.isEmpty() ? getIdentifierWithQuoting(tableName)
        : getIdentifierWithQuoting(nameSpace) + "." + getIdentifierWithQuoting(tableName));
  }

  protected AutoCloseableIterator<JsonNode> queryTable(final Database database, final String sqlQuery) {
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final Stream<JsonNode> stream = database.query(sqlQuery);
        return AutoCloseableIterators.fromStream(stream);
      } catch (final Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

}
