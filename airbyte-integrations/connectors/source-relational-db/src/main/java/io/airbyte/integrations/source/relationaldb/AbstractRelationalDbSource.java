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
import io.airbyte.protocol.models.CommonField;
import io.airbyte.protocol.models.Field;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.StringJoiner;
import java.util.stream.Collectors;
import java.util.stream.Stream;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public abstract class AbstractRelationalDbSource<DataType, Database extends SqlDatabase> extends
    AbstractDbSource<DataType, Database> implements Source {

  private static final Logger LOGGER = LoggerFactory.getLogger(AbstractRelationalDbSource.class);

  @Override
  public AutoCloseableIterator<JsonNode> queryTableFullRefresh(Database database,
                                                               List<String> columnNames,
                                                               String schemaName,
                                                               String tableName) {
    LOGGER.info("Queueing query for table: {}", tableName);
    return queryTable(database, String.format("SELECT %s FROM %s",
        enquoteIdentifierList(columnNames),
        getFullTableName(schemaName, tableName)));
  }

  protected String getIdentifierWithQuoting(String identifier) {
    return getQuoteString() + identifier + getQuoteString();
  }

  protected String enquoteIdentifierList(List<String> identifiers) {
    final StringJoiner joiner = new StringJoiner(",");
    for (String identifier : identifiers) {
      joiner.add(getIdentifierWithQuoting(identifier));
    }
    return joiner.toString();
  }

  protected String getFullTableName(String nameSpace, String tableName) {
    return (nameSpace == null || nameSpace.isEmpty() ? getIdentifierWithQuoting(tableName)
        : getIdentifierWithQuoting(nameSpace) + "." + getIdentifierWithQuoting(tableName));
  }

  protected AutoCloseableIterator<JsonNode> queryTable(Database database, String sqlQuery) {
    return AutoCloseableIterators.lazyIterator(() -> {
      try {
        final Stream<JsonNode> stream = database.query(sqlQuery);
        return AutoCloseableIterators.fromStream(stream);
      } catch (Exception e) {
        throw new RuntimeException(e);
      }
    });
  }

}
