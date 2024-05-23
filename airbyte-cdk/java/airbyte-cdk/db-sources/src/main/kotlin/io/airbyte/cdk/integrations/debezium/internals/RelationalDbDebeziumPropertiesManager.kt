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
    catalog: ConfiguredAirbyteCatalog
) : DebeziumPropertiesManager(properties, config, catalog) {
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
        config: JsonNode?
    ): Properties {
        val properties = Properties()

        // table selection
        properties.setProperty("table.include.list", getTableIncludelist(catalog))
        // column selection
        properties.setProperty("column.include.list", getColumnIncludeList(catalog))

        return properties
    }

    companion object {
        fun getTableIncludelist(catalog: ConfiguredAirbyteCatalog): String {
            // Turn "stream": {
            // "namespace": "schema1"
            // "name": "table1
            // },
            // "stream": {
            // "namespace": "schema2"
            // "name": "table2
            // } -------> info "schema1.table1, schema2.table2"

            return catalog.streams
                .stream()
                .filter { s: ConfiguredAirbyteStream -> s.syncMode == SyncMode.INCREMENTAL }
                .map { obj: ConfiguredAirbyteStream -> obj.stream }
                .map { stream: AirbyteStream ->
                    stream.namespace + "." + stream.name
                } // debezium needs commas escaped to split properly
                .map { x: String -> StringUtils.escape(Pattern.quote(x), ",".toCharArray(), "\\,") }
                .collect(Collectors.joining(","))
        }

        fun getColumnIncludeList(catalog: ConfiguredAirbyteCatalog): String {
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
                .stream()
                .filter { s: ConfiguredAirbyteStream -> s.syncMode == SyncMode.INCREMENTAL }
                .map { obj: ConfiguredAirbyteStream -> obj.stream }
                .map { s: AirbyteStream ->
                    val fields = parseFields(s.jsonSchema["properties"].fieldNames())
                    Pattern.quote(s.namespace + "." + s.name) +
                        (if (StringUtils.isNotBlank(fields)) "\\.$fields" else "")
                }
                .map { x: String -> StringUtils.escape(x, ",".toCharArray(), "\\,") }
                .collect(Collectors.joining(","))
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
