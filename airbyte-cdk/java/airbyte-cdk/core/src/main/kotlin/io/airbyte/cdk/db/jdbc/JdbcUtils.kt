/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db.jdbc

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.Maps
import io.airbyte.commons.exceptions.ConfigErrorException
import java.sql.JDBCType
import org.jooq.JSONFormat

object JdbcUtils {
    // config parameters in alphabetical order
    const val CONNECTION_PROPERTIES_KEY: String = "connection_properties"
    const val DATABASE_KEY: String = "database"
    const val ENCRYPTION_KEY: String = "encryption"
    const val HOST_KEY: String = "host"
    @JvmField val HOST_LIST_KEY: List<String> = listOf("host")
    const val JDBC_URL_KEY: String = "jdbc_url"
    const val JDBC_URL_PARAMS_KEY: String = "jdbc_url_params"
    const val PASSWORD_KEY: String = "password"
    const val PORT_KEY: String = "port"

    @JvmField val PORT_LIST_KEY: List<String> = listOf("port")
    const val SCHEMA_KEY: String = "schema"

    // NOTE: this is the plural version of SCHEMA_KEY
    const val SCHEMAS_KEY: String = "schemas"
    const val SSL_KEY: String = "ssl"
    val SSL_MODE_DISABLE: List<String> = listOf("disable", "disabled")
    const val SSL_MODE_KEY: String = "ssl_mode"
    const val TLS_KEY: String = "tls"
    const val USERNAME_KEY: String = "username"
    const val MODE_KEY: String = "mode"
    const val AMPERSAND: String = "&"
    const val EQUALS: String = "="

    // An estimate for how much additional data in sent over the wire due to conversion of source
    // data
    // into {@link AirbyteMessage}. This is due to
    // the fact that records are in JSON format and all database fields are converted to Strings.
    // Currently, this is used in the logic for emitting
    // estimate trace messages.
    const val PLATFORM_DATA_INCREASE_FACTOR: Int = 2
    val ALLOWED_CURSOR_TYPES: Set<JDBCType> =
        java.util.Set.of(
            JDBCType.TIMESTAMP_WITH_TIMEZONE,
            JDBCType.TIMESTAMP,
            JDBCType.TIME_WITH_TIMEZONE,
            JDBCType.TIME,
            JDBCType.DATE,
            JDBCType.TINYINT,
            JDBCType.SMALLINT,
            JDBCType.INTEGER,
            JDBCType.BIGINT,
            JDBCType.FLOAT,
            JDBCType.DOUBLE,
            JDBCType.REAL,
            JDBCType.NUMERIC,
            JDBCType.DECIMAL,
            JDBCType.NVARCHAR,
            JDBCType.VARCHAR,
            JDBCType.LONGVARCHAR
        )
    @JvmStatic val defaultSourceOperations: JdbcSourceOperations = JdbcSourceOperations()

    @JvmStatic
    val defaultJSONFormat: JSONFormat = JSONFormat().recordFormat(JSONFormat.RecordFormat.OBJECT)

    @JvmStatic
    fun getFullyQualifiedTableName(schemaName: String?, tableName: String): String {
        return if (schemaName != null) "$schemaName.$tableName" else tableName
    }

    @JvmStatic
    @JvmOverloads
    fun parseJdbcParameters(
        config: JsonNode,
        jdbcUrlParamsKey: String?,
        delimiter: String = "&"
    ): Map<String, String> {
        return if (config.has(jdbcUrlParamsKey)) {
            parseJdbcParameters(config[jdbcUrlParamsKey].asText(), delimiter)
        } else {
            Maps.newHashMap()
        }
    }

    @JvmStatic
    @JvmOverloads
    fun parseJdbcParameters(
        jdbcPropertiesString: String,
        delimiter: String = "&"
    ): Map<String, String> {
        val parameters: MutableMap<String, String> = HashMap()
        if (!jdbcPropertiesString.isBlank()) {
            val keyValuePairs =
                jdbcPropertiesString
                    .split(delimiter.toRegex())
                    .dropLastWhile { it.isEmpty() }
                    .toTypedArray()
            for (kv in keyValuePairs) {
                val split = kv.split("=".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()
                if (split.size == 2) {
                    parameters[split[0]] = split[1]
                } else {
                    throw ConfigErrorException(
                        "jdbc_url_params must be formatted as 'key=value' pairs separated by the symbol '&'. (example: key1=value1&key2=value2&key3=value3). Got " +
                            jdbcPropertiesString
                    )
                }
            }
        }
        return parameters
    }

    /**
     * Checks that SSL_KEY has not been set or that an SSL_KEY is set and value can be mapped to
     * true (e.g. non-zero integers, string true, etc)
     *
     * @param config A configuration used to check Jdbc connection
     * @return true: if ssl has not been set and ssl mode not equals disabled or it has been set
     * with true, false: in all other cases
     */
    @JvmStatic
    fun useSsl(config: JsonNode): Boolean {
        return if (!config.has(SSL_KEY)) {
            if (config.has(SSL_MODE_KEY) && config[SSL_MODE_KEY].has(MODE_KEY)) {
                !SSL_MODE_DISABLE.contains(config[SSL_MODE_KEY][MODE_KEY].asText())
            } else true
        } else config[SSL_KEY].asBoolean()
    }
}
