/*
 * Copyright (c) 2021 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.jdbc;

import io.airbyte.integrations.source.relationaldb.FieldSizeEstimator;
import io.airbyte.protocol.models.CommonField;
import java.sql.JDBCType;
import java.util.Optional;

public class JdbcFieldSizeEstimator implements FieldSizeEstimator<JDBCType> {

  @Override
  public long getByteSize(final CommonField<JDBCType> field) {
    final Optional<Integer> columnSize = field.getColumnSize();

    switch (field.getType()) {
      case NULL, BOOLEAN -> {
        return 1L;
      }
      case BIT -> {
        return columnSize.orElse(1);
      }
      case DATE, TIME, TIMESTAMP, TIME_WITH_TIMEZONE, TIMESTAMP_WITH_TIMEZONE -> {
        return 50L;
      }
      case TINYINT, SMALLINT, INTEGER -> {
        return 4L;
      }
      case FLOAT, DOUBLE, REAL, NUMERIC, DECIMAL -> {
        return 8L;
      }
      case BIGINT -> {
        return 80L;
      }
      case CHAR, VARCHAR, LONGVARCHAR, NCHAR, NVARCHAR, LONGNVARCHAR -> {
        return columnSize.orElse(1000);
      }
      case BLOB, BINARY, VARBINARY, LONGVARBINARY -> {
        return columnSize.orElse(5000);
      }
      default -> {
        return 1000L;
      }
    }
  }

}
