/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.test.fixtures.legacy

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.v0.AirbyteCatalog
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog

interface Source : Integration {
    /**
     * Discover the current schema in the source.
     *
     * @param config
     * - integration-specific configuration object as json. e.g. { "username": "airbyte",
     * "password": "super secure" }
     * @return Description of the schema.
     * @throws Exception
     * - any exception.
     */
    @Throws(Exception::class) fun discover(config: JsonNode): AirbyteCatalog

    /**
     * Return a iterator of messages pulled from the source.
     *
     * @param config
     * - integration-specific configuration object as json. e.g. { "username": "airbyte",
     * "password": "super secure" }
     * @param catalog
     * - schema of the incoming messages.
     * @param state
     * - state of the incoming messages.
     * @return [AutoCloseableIterator] that produces message. The iterator will be consumed until no
     * records remain or until an exception is thrown. [AutoCloseableIterator.close] will always be
     * called once regardless of success or failure.
     * @throws Exception
     * - any exception.
     */
    @Throws(Exception::class)
    fun read(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        state: JsonNode?
    ): AutoCloseableIterator<AirbyteMessage>

    /**
     * Returns a collection of iterators of messages pulled from the source, each representing a
     * "stream".
     *
     * @param config
     * - integration-specific configuration object as json. e.g. { "username": "airbyte",
     * "password": "super secure" }
     * @param catalog
     * - schema of the incoming messages.
     * @param state
     * - state of the incoming messages.
     * @return The collection of [AutoCloseableIterator] instances that produce messages for each
     * configured "stream"
     * @throws Exception
     * - any exception
     */
    @Throws(Exception::class)
    fun readStreams(
        config: JsonNode,
        catalog: ConfiguredAirbyteCatalog,
        state: JsonNode?
    ): Collection<AutoCloseableIterator<AirbyteMessage>>? {
        return listOf(read(config, catalog, state))
    }
}
