/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.components.debezium

import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.SyncMode
import org.codehaus.plexus.util.StringUtils
import java.util.regex.Pattern

open class RelationalConfigBuilder<B : RelationalConfigBuilder<B>> : ConfigBuilder<B>() {
    init {
        // https://debezium.io/documentation/reference/2.2/connectors/postgresql.html#postgresql-property-max-queue-size-in-bytes
        props.setProperty("max.queue.size.in.bytes", (256L * 1024 * 1024).toString())
    }

    fun withDatabaseHost(host: String): B {
        return with("database.hostname", host)
    }

    fun withDatabasePort(port: Int): B {
        return with("database.port", port.toString())
    }

    fun withDatabaseUser(user: String): B {
        return with("database.user", user)
    }

    fun withDatabasePassword(password: String): B {
        return with("database.password", password)
    }

    fun withDatabaseName(name: String): B {
        return with("database.dbname", name)
                .withDebeziumName(name)
    }

    fun withCatalog(catalog: ConfiguredAirbyteCatalog): B {
        val incrementalStreams: List<AirbyteStream> = catalog.streams
            .filter { cs -> cs.syncMode == SyncMode.INCREMENTAL }
            .map { cs -> cs.stream }
        val tableIncludeList = incrementalStreams.map { s ->
            Pattern.quote("${s.namespace}.${s.name}")
        }
        val columnIncludeList: List<String> = incrementalStreams.map { s ->
            val prefix = Pattern.quote("${s.namespace}.${s.name}")
            val suffix = s.jsonSchema["properties"].fieldNames().asSequence().map(Pattern::quote).joinToString("|")
            "$prefix\\.($suffix)"
        }
        return with("table.include.list", joinIncludeList(tableIncludeList))
                .with("column.include.list", joinIncludeList(columnIncludeList))
    }

    private fun joinIncludeList(includes: List<String> ): String = includes
            .map { id: String -> StringUtils.escape(id, ",".toCharArray(), "\\,") }
            .joinToString(",")

}
