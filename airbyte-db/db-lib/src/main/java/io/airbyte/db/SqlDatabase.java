/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.db;

import com.fasterxml.jackson.databind.JsonNode;
import io.airbyte.commons.functional.CheckedFunction;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.SQLException;
import java.util.stream.Stream;
import javax.sql.RowSet;
import org.apache.commons.lang3.tuple.Pair;
import org.postgresql.core.Tuple;

public abstract class SqlDatabase extends AbstractDatabase {

  public abstract void execute(String sql) throws Exception;

  public abstract Stream<JsonNode> unsafeQuery(String sql, String... params) throws Exception;

  public abstract Stream<Tuple> unsafeQueryRS(String sql, String... params) throws Exception;

  public abstract CheckedFunction<Pair<Tuple, ResultSetMetaData>, JsonNode, SQLException> getRecordTransform();

}
