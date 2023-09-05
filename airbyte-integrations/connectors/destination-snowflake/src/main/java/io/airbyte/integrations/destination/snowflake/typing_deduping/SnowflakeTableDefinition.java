/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import java.util.LinkedHashMap;

/**
 * @param columns Map from column name to type. Type is a plain string because
 *        {@link net.snowflake.client.jdbc.SnowflakeType} doesn't actually have all the types that
 *        Snowflake supports.
 */
// TODO fields for columns + indexes... or other stuff we want to set?
public record SnowflakeTableDefinition(LinkedHashMap<String, String> columns) {}
