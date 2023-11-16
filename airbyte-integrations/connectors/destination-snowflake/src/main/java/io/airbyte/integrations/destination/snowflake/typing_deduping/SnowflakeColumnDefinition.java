/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

/**
 * isNullable is only used to execute a migration away from an older version of
 * destination-snowflake, where we created PK columns as NOT NULL. This caused a lot of problems
 * because many sources emit null PKs. We may want to remove this field eventually.
 */
public record SnowflakeColumnDefinition(String type, boolean isNullable) {

  @Deprecated
  public boolean isNullable() {
    return isNullable;
  }

}
