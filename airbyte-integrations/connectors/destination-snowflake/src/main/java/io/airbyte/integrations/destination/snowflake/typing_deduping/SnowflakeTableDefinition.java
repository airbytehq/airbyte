/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.typing_deduping;

import java.util.LinkedHashMap;

public record SnowflakeTableDefinition(LinkedHashMap<String, SnowflakeColumnDefinition> columns) {}
