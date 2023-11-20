/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

/**
 * type is notably _not_ a {@link net.snowflake.client.jdbc.SnowflakeType}. That enum doesn't
 * contain all the types that snowflake supports (specifically NUMBER).
 */
public record SnowflakeColumn(String name, String type) {}
