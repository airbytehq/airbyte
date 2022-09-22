/*
 * Copyright (c) 2022 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.config.persistence;

import org.jooq.Condition;
import org.jooq.Field;

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

}
