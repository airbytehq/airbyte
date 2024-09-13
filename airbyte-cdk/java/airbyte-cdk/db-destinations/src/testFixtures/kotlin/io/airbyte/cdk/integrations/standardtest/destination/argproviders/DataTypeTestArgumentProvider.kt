/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination.argproviders

import io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.util.ArgumentProviderUtil
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.stream.Stream
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider

private val LOGGER = KotlinLogging.logger {}

class DataTypeTestArgumentProvider : ArgumentsProvider {
    private lateinit var protocolVersion: ProtocolVersion

    @Throws(Exception::class)
    override fun provideArguments(context: ExtensionContext): Stream<out Arguments> {
        protocolVersion = ArgumentProviderUtil.getProtocolVersion(context)
        return Stream.of(
            getArguments(BASIC_TEST),
            getArguments(ARRAY_TEST),
            getArguments(OBJECT_TEST),
            getArguments(OBJECT_WITH_ARRAY_TEST)
        )
    }

    private fun getArguments(testConfig: CatalogMessageTestConfigWithCompatibility): Arguments {
        return Arguments.of(
            testConfig.getMessageFileVersion(protocolVersion),
            testConfig.getCatalogFileVersion(protocolVersion),
            testConfig.testCompatibility
        )
    }

    @JvmRecord
    data class TestCompatibility(
        val requireBasicCompatibility: Boolean,
        val requireArrayCompatibility: Boolean,
        val requireObjectCompatibility: Boolean
    ) {
        fun isTestCompatible(
            supportBasicDataTypeTest: Boolean,
            supportArrayDataTypeTest: Boolean,
            supportObjectDataTypeTest: Boolean
        ): Boolean {
            LOGGER.info("---- Data type test compatibility ----")
            LOGGER.info("| Data type test | Require | Support |")
            LOGGER.info(
                "| Basic test     | {}   | {}   |",
                (if (requireBasicCompatibility) "true " else "false"),
                (if (supportBasicDataTypeTest) "true " else "false")
            )
            LOGGER.info(
                "| Array test     | {}   | {}   |",
                (if (requireArrayCompatibility) "true " else "false"),
                (if (supportArrayDataTypeTest) "true " else "false")
            )
            LOGGER.info(
                "| Object test    | {}   | {}   |",
                (if (requireObjectCompatibility) "true " else "false"),
                (if (supportObjectDataTypeTest) "true " else "false")
            )
            LOGGER.info("--------------------------------------")

            if (requireBasicCompatibility && !supportBasicDataTypeTest) {
                LOGGER.warn(
                    "The destination doesn't support required Basic data type test. The test is skipped!"
                )
                return false
            }
            if (requireArrayCompatibility && !supportArrayDataTypeTest) {
                LOGGER.warn(
                    "The destination doesn't support required Array data type test. The test is skipped!"
                )
                return false
            }
            if (requireObjectCompatibility && !supportObjectDataTypeTest) {
                LOGGER.warn(
                    "The destination doesn't support required Object data type test. The test is skipped!"
                )
                return false
            }

            return true
        }
    }

    class CatalogMessageTestConfigWithCompatibility(
        catalogFile: String,
        messageFile: String,
        val testCompatibility: TestCompatibility
    ) : DataArgumentsProvider.CatalogMessageTestConfigPair(catalogFile, messageFile)

    companion object {

        const val INTEGER_TYPE_CATALOG: String = "data_type_integer_type_test_catalog.json"
        const val NUMBER_TYPE_CATALOG: String = "data_type_number_type_test_catalog.json"
        const val NAN_TYPE_MESSAGE: String = "nan_type_test_message.txt"
        const val INFINITY_TYPE_MESSAGE: String = "nan_type_test_message.txt"
        val BASIC_TEST: CatalogMessageTestConfigWithCompatibility =
            CatalogMessageTestConfigWithCompatibility(
                "data_type_basic_test_catalog.json",
                "data_type_basic_test_messages.txt",
                TestCompatibility(true, false, false)
            )
        val ARRAY_TEST: CatalogMessageTestConfigWithCompatibility =
            CatalogMessageTestConfigWithCompatibility(
                "data_type_array_test_catalog.json",
                "data_type_array_test_messages.txt",
                TestCompatibility(true, true, false)
            )
        val OBJECT_TEST: CatalogMessageTestConfigWithCompatibility =
            CatalogMessageTestConfigWithCompatibility(
                "data_type_object_test_catalog.json",
                "data_type_object_test_messages.txt",
                TestCompatibility(true, false, true)
            )
        val OBJECT_WITH_ARRAY_TEST: CatalogMessageTestConfigWithCompatibility =
            CatalogMessageTestConfigWithCompatibility(
                "data_type_array_object_test_catalog.json",
                "data_type_array_object_test_messages.txt",
                TestCompatibility(true, true, true)
            )
    }
}
