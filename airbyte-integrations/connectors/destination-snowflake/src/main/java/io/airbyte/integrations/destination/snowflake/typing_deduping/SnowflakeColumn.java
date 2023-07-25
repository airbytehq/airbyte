package io.airbyte.integrations.destination.snowflake.typing_deduping;

import net.snowflake.client.jdbc.SnowflakeType;

public record SnowflakeColumn(String name, SnowflakeType type) {
}
