/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination.argproviders

import io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.util.ArgumentProviderUtil
import java.util.stream.Stream
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider

class NumberDataTypeTestArgumentProvider : ArgumentsProvider {
    private lateinit var protocolVersion: ProtocolVersion

    @Throws(Exception::class)
    override fun provideArguments(context: ExtensionContext): Stream<out Arguments> {
        protocolVersion = ArgumentProviderUtil.getProtocolVersion(context)
        return Stream.of(
            getArguments(NUMBER_DATA_TYPE_TEST_CATALOG, NUMBER_DATA_TYPE_TEST_MESSAGES),
            getArguments(NUMBER_DATA_TYPE_ARRAY_TEST_CATALOG, NUMBER_DATA_TYPE_ARRAY_TEST_MESSAGES)
        )
    }

    private fun getArguments(catalogFile: String, messageFile: String): Arguments {
        return Arguments.of(
            ArgumentProviderUtil.prefixFileNameByVersion(catalogFile, protocolVersion),
            ArgumentProviderUtil.prefixFileNameByVersion(messageFile, protocolVersion)
        )
    }

    companion object {
        const val NUMBER_DATA_TYPE_TEST_CATALOG: String = "number_data_type_test_catalog.json"
        const val NUMBER_DATA_TYPE_TEST_MESSAGES: String = "number_data_type_test_messages.txt"
        const val NUMBER_DATA_TYPE_ARRAY_TEST_CATALOG: String =
            "number_data_type_array_test_catalog.json"
        const val NUMBER_DATA_TYPE_ARRAY_TEST_MESSAGES: String =
            "number_data_type_array_test_messages.txt"
    }
}
