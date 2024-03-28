/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base.spec_modification

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.base.Source
import io.airbyte.commons.util.AutoCloseableIterator
import io.airbyte.protocol.models.v0.*

/**
 * In some cases we want to prune or mutate the spec for an existing source. The common case is that
 * we want to remove features that are not appropriate for some reason. e.g. In cloud, we do not
 * want to allow users to send data unencrypted.
 */
abstract class SpecModifyingSource(private val source: Source) : Source {
    @Throws(Exception::class)
    abstract fun modifySpec(originalSpec: ConnectorSpecification): ConnectorSpecification

    @Throws(Exception::class)
    override fun spec(): ConnectorSpecification {
        return modifySpec(source.spec())
    }

    @Throws(Exception::class)
    override fun check(config: JsonNode): AirbyteConnectionStatus? {
        return source.check(config)
    }

    @Throws(Exception::class)
    override fun discover(config: JsonNode): AirbyteCatalog {
        return source.discover(config)
    }

    @Throws(Exception::class)
    override fun read(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        state: JsonNode?
    ): AutoCloseableIterator<AirbyteMessage> {
        return source.read(config, catalog, state)
    }

    @Throws(Exception::class)
    override fun readStreams(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        state: JsonNode?
    ): Collection<AutoCloseableIterator<AirbyteMessage>>? {
        return source.readStreams(config, catalog, state)
    }
}
