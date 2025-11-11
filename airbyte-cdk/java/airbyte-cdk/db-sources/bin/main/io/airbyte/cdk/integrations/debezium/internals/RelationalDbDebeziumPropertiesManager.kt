/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.debezium.internals

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.SyncMode
import java.util.*
import java.util.regex.Pattern
import java.util.stream.Collectors
import java.util.stream.StreamSupport
import org.codehaus.plexus.util.StringUtils

class RelationalDbDebeziumPropertiesManager(
    properties: Properties,
    config: JsonNode,
    catalog: ConfiguredAirbyteCatalog,
    completedStreamNames: List<String>
) : DebeziumPropertiesManager(properties, config, catalog, completedStreamNames) {
    override fun getConnectionConfiguration(config: JsonNode): Properties {
        val properties = Properties()

        // db connection configuration
        properties.setProperty("database.hostname", config[JdbcUtils.HOST_KEY].asText())
        properties.setProperty("database.port", config[JdbcUtils.PORT_KEY].asText())
        properties.setProperty("database.user", config[JdbcUtils.USERNAME_KEY].asText())
        properties.setProperty("database.dbname", config[JdbcUtils.DATABASE_KEY].asText())

        if (config.has(JdbcUtils.PASSWORD_KEY)) {
            properties.setProperty("database.password", config[JdbcUtils.PASSWORD_KEY].asText())
        }

        return properties
    }

    override fun getName(config: JsonNode): String {
        return config[JdbcUtils.DATABASE_KEY].asText()
    }

    override fun getIncludeConfiguration(
        catalog: ConfiguredAirbyteCatalog,
        config: JsonNode?,
        streamNames: List<String>
    ): Properties {
        val properties = Properties()

        // table selection
        properties.setProperty("table.include.list", getTableIncludelist(catalog, streamNames))
        // column selection
        properties.setProperty("column.include.list", getColumnIncludeList(catalog, streamNames))

        return properties
    }

    companion object {
        fun getTableIncludelist(
            catalog: ConfiguredAirbyteCatalog,
            completedStreamNames: List<String>
        ): String {
            // Turn "stream": {
            // "namespace": "schema1"
            // "name": "table1
            // },
            // "stream": {
            // "namespace": "schema2"
            // "name": "table2
            // } -------> info "schema1.table1, schema2.table2"

            return catalog.streams
                .filter { s: ConfiguredAirbyteStream -> s.syncMode == SyncMode.INCREMENTAL }
                .map { obj: ConfiguredAirbyteStream -> obj.stream }
                .map { stream: AirbyteStream -> stream.namespace + "." + stream.name }
                .filter { streamName: String -> completedStreamNames.contains(streamName) }
                // debezium needs commas escaped to split properly
                .joinToString(",") { x: String ->
                    StringUtils.escape(Pattern.quote(x), ",".toCharArray(), "\\,")
                }
        }

        fun getColumnIncludeList(
            catalog: ConfiguredAirbyteCatalog,
            completedStreamNames: List<String>
        ): String {
            // Turn "stream": {
            // "namespace": "schema1"
            // "name": "table1"
            // "jsonSchema": {
            // "properties": {
            // "column1": {
            // },
            // "column2": {
            // }
            // }
            // }
            // } -------> info "schema1.table1.(column1 | column2)"

            return catalog.streams
                .filter { s: ConfiguredAirbyteStream -> s.syncMode == SyncMode.INCREMENTAL }
                .map { obj: ConfiguredAirbyteStream -> obj.stream }
                .filter { stream: AirbyteStream ->
                    completedStreamNames.contains(stream.namespace + "." + stream.name)
                }
                .map { s: AirbyteStream ->
                    val fields = parseFields(s.jsonSchema["properties"].fieldNames())
                    Pattern.quote(s.namespace + "." + s.name) +
                        (if (StringUtils.isNotBlank(fields)) "\\.$fields" else "")
                }
                .joinToString(",") { x: String -> StringUtils.escape(x, ",".toCharArray(), "\\,") }
        }

        private fun parseFields(fieldNames: Iterator<String>?): String {
            if (fieldNames == null || !fieldNames.hasNext()) {
                return ""
            }
            val iter = Iterable { fieldNames }
            return StreamSupport.stream(iter.spliterator(), false)
                .map { f: String -> Pattern.quote(f) }
                .collect(Collectors.joining("|", "(", ")"))
        }
    }
}
