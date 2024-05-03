/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.singlestore.typing_deduping;

import static io.airbyte.cdk.integrations.base.JavaBaseConstants.COLUMN_NAME_DATA;
import static org.jooq.impl.DSL.*;
import static org.jooq.impl.SQLDataType.BOOLEAN;
import static org.jooq.impl.SQLDataType.VARCHAR;

import io.airbyte.integrations.base.destination.typing_deduping.ColumnId;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import org.jooq.DataType;
import org.jooq.Field;
import org.jooq.impl.CustomField;
import org.jooq.impl.DSL;

public final class DslUtils {

  private DslUtils() {}

  /**
   * Cast to target data type with default error behavior.
   *
   * @param field to cast
   * @param type to cast to
   * @param force if true use forceful casting
   */
  public static Field<String> cast(@Nullable Field<?> field, @NotNull DataType<?> type, boolean force) {
    if (type == BOOLEAN) {
      return CustomField.of("cast_bool", VARCHAR, ctx -> ctx.visit(DSL.field("({0} = 'TRUE')", field)));
    }
    final String sql = force ? "({0} !:> {1})" : "({0} :> {1})";
    final Field<?> typeField = DSL.field(type.getCastTypeName());
    return CustomField.of("cast", VARCHAR, ctx -> ctx.visit(DSL.field(sql, field, typeField)));
  }

  public static Field<Object> extractColumnAsString(final ColumnId column) {
    return field(String.format("json_extract_string(%s, {0})", COLUMN_NAME_DATA), val(column.getOriginalName()));
  }

  public static Field<?> jsonBuildObject(Field<?>... arguments) {
    return function("JSON_BUILD_OBJECT", SingleStoreSqlGenerator.JSON_TYPE, arguments);
  }

}
