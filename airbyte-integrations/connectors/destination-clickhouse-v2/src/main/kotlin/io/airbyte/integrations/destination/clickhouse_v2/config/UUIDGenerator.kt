package io.airbyte.integrations.destination.clickhouse_v2.config

import com.github.f4b6a3.uuid.alt.GUID
import jakarta.inject.Singleton
import java.util.UUID

@Singleton
class UUIDGenerator {
    fun v7(): UUID = GUID.v7().toUUID()
}
