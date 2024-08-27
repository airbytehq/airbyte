/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination.argproviders

import java.util.stream.Stream
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider

/**
 * Class encapsulating all arguments required for Standard Destination Tests.
 *
 * All files defined here can be found in src/main/resources of this package.
 */
class DataArgumentsProvider : ArgumentsProvider {
    @Throws(Exception::class)
    override fun provideArguments(context: ExtensionContext): Stream<out Arguments> {
        return Stream.of(
            Arguments.of(EXCHANGE_RATE_CONFIG.messageFile, EXCHANGE_RATE_CONFIG.catalogFile),
            Arguments.of(EDGE_CASE_CONFIG.messageFile, EDGE_CASE_CONFIG.catalogFile)
        )
    }

    open class CatalogMessageTestConfigPair(val catalogFile: String, val messageFile: String)

    companion object {
        @JvmField
        val EXCHANGE_RATE_CONFIG: CatalogMessageTestConfigPair =
            CatalogMessageTestConfigPair("exchange_rate_catalog.json", "exchange_rate_messages.txt")
        val EDGE_CASE_CONFIG: CatalogMessageTestConfigPair =
            CatalogMessageTestConfigPair("edge_case_catalog.json", "edge_case_messages.txt")
        val NAMESPACE_CONFIG: CatalogMessageTestConfigPair =
            CatalogMessageTestConfigPair("namespace_catalog.json", "namespace_messages.txt")
    }
}
