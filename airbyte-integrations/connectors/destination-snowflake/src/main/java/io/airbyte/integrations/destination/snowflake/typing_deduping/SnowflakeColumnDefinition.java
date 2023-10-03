/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

public record SnowflakeColumnDefinition(String type, boolean isNullable) {}
