package io.airbyte.integrations.destination.clickhouse_v2.model

import com.clickhouse.data.ClickHouseDataType

data class AlterationSummary(
    val added: Map<String, ClickHouseDataType>,
    val modified: Map<String, ClickHouseDataType>,
    val deleted: Map<String, ClickHouseDataType>,
)
