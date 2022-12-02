/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import static org.jooq.impl.DSL.select;

import java.util.UUID;
import org.jooq.Condition;
import org.jooq.DSLContext;
import org.jooq.Field;
import org.jooq.Record;
import org.jooq.TableField;
import org.jooq.impl.TableImpl;

public class PersistenceHelpers {

  /**
   * Helper function to handle null or equal case for the optional strings
   *
   * We need to have an explicit check for null values because NULL != "str" is NULL, not a boolean.
   *
   * @param field the targeted field
   * @param value the value to check
   * @return The Condition that performs the desired check
   */
  public static Condition isNullOrEquals(final Field<String> field, final String value) {
    return value != null ? field.eq(value) : field.isNull();
  }

  /**
   * Helper to delete records from the database
   *
   * @param table the table to delete from
   * @param keyColumn the column to use as a key
   * @param configId the id of the object to delete, must be from the keyColumn
   * @param ctx the db context to use
   */
  public static <T extends Record> void deleteConfig(final TableImpl<T> table,
                                                     final TableField<T, UUID> keyColumn,
                                                     final UUID configId,
                                                     final DSLContext ctx) {
    final boolean isExistingConfig = ctx.fetchExists(select()
        .from(table)
        .where(keyColumn.eq(configId)));

    if (isExistingConfig) {
      ctx.deleteFrom(table)
          .where(keyColumn.eq(configId))
          .execute();
    }
  }

}
