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

/**
 * Class encapsulating all arguments required for Standard Destination Tests.
 *
 * All files defined here can be found in src/main/resources of this package.
 */
class DataArgumentsProvider : ArgumentsProvider {
    @Throws(Exception::class)
    override fun provideArguments(context: ExtensionContext): Stream<out Arguments> {
        val protocolVersion = ArgumentProviderUtil.getProtocolVersion(context)
        return Stream.of(
            Arguments.of(
                EXCHANGE_RATE_CONFIG.getMessageFileVersion(protocolVersion),
                EXCHANGE_RATE_CONFIG.getCatalogFileVersion(protocolVersion)
            ),
            Arguments.of(
                EDGE_CASE_CONFIG.getMessageFileVersion(protocolVersion),
                EDGE_CASE_CONFIG.getCatalogFileVersion(protocolVersion)
            ) // todo - need to use the new protocol to capture this.
            // Arguments.of("stripe_messages.txt", "stripe_schema.json")
            )
    }

    open class CatalogMessageTestConfigPair(val catalogFile: String, val messageFile: String) {
        fun getCatalogFileVersion(protocolVersion: ProtocolVersion): String {
            return ArgumentProviderUtil.prefixFileNameByVersion(catalogFile, protocolVersion)
        }

        fun getMessageFileVersion(protocolVersion: ProtocolVersion): String {
            return ArgumentProviderUtil.prefixFileNameByVersion(messageFile, protocolVersion)
        }
    }

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
