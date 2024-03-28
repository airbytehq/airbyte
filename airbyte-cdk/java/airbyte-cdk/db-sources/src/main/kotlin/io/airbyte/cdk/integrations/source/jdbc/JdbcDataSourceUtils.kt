/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.jdbc

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.JdbcUtils
import io.airbyte.cdk.db.jdbc.JdbcUtils.parseJdbcParameters
import io.airbyte.commons.map.MoreMaps

object JdbcDataSourceUtils {
    const val DEFAULT_JDBC_PARAMETERS_DELIMITER: String = "&"

    /**
     * Validates for duplication parameters
     *
     * @param customParameters custom connection properties map as specified by each Jdbc source
     * @param defaultParameters connection properties map as specified by each Jdbc source
     * @throws IllegalArgumentException
     */
    @JvmStatic
    fun assertCustomParametersDontOverwriteDefaultParameters(
        customParameters: Map<String, String>,
        defaultParameters: Map<String, String>
    ) {
        for (key in defaultParameters.keys) {
            require(
                !(customParameters.containsKey(key) &&
                    customParameters[key] != defaultParameters[key])
            ) { "Cannot overwrite default JDBC parameter $key" }
        }
    }

    /**
     * Retrieves connection_properties from config and also validates if custom jdbc_url parameters
     * overlap with the default properties
     *
     * @param config A configuration used to check Jdbc connection
     * @return A mapping of connection properties
     */
    fun getConnectionProperties(config: JsonNode): Map<String, String> {
        return getConnectionProperties(config, DEFAULT_JDBC_PARAMETERS_DELIMITER)
    }

    fun getConnectionProperties(config: JsonNode, parameterDelimiter: String): Map<String, String> {
        val customProperties =
            parseJdbcParameters(config, JdbcUtils.JDBC_URL_PARAMS_KEY, parameterDelimiter)
        val defaultProperties = getDefaultConnectionProperties(config)
        assertCustomParametersDontOverwriteDefaultParameters(customProperties, defaultProperties)
        return MoreMaps.merge(customProperties, defaultProperties)
    }

    /**
     * Retrieves default connection_properties from config
     *
     * TODO: make this method abstract and add parity features to destination connectors
     *
     * @param config A configuration used to check Jdbc connection
     * @return A mapping of the default connection properties
     */
    @JvmStatic
    fun getDefaultConnectionProperties(config: JsonNode): Map<String, String> {
        // NOTE that Postgres returns an empty map for some reason?
        return parseJdbcParameters(
            config,
            "connection_properties",
            DEFAULT_JDBC_PARAMETERS_DELIMITER
        )
    }
}
