package io.airbyte.integrations.destination.snowflake.typing_deduping;

import java.util.List;

// TODO fields for columns + indexes... or other stuff we want to set?
public record SnowflakeTableDefinition(List<SnowflakeColumn> columns) {
}
