/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.source.jdbc

import io.airbyte.commons.json.Jsons
import java.util.function.Consumer
import org.assertj.core.api.AssertionsForClassTypes
import org.junit.Assert
import org.junit.jupiter.api.Assertions
import org.junit.jupiter.api.Test

class JdbcDataSourceUtilsTest {
    @Test
    fun test() {
        val validConfigString =
            "{\"jdbc_url_params\":\"key1=val1&key3=key3\",\"connection_properties\":\"key1=val1&key2=val2\"}"
        val validConfig = Jsons.deserialize(validConfigString)
        val connectionProperties = JdbcDataSourceUtils.getConnectionProperties(validConfig)
        val validKeys = listOf("key1", "key2", "key3")
        validKeys.forEach(
            Consumer { key: String -> Assert.assertTrue(connectionProperties.containsKey(key)) }
        )

        // For an invalid config, there is a conflict betweeen the values of keys in jdbc_url_params
        // and
        // connection_properties
        val invalidConfigString =
            "{\"jdbc_url_params\":\"key1=val2&key3=key3\",\"connection_properties\":\"key1=val1&key2=val2\"}"
        val invalidConfig = Jsons.deserialize(invalidConfigString)
        val exception: Exception =
            Assertions.assertThrows(IllegalArgumentException::class.java) {
                JdbcDataSourceUtils.getConnectionProperties(invalidConfig)
            }

        val expectedMessage = "Cannot overwrite default JDBC parameter key1"
        AssertionsForClassTypes.assertThat(expectedMessage == exception.message)
    }
}
