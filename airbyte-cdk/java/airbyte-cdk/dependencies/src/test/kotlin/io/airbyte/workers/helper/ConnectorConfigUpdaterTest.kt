/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.helper

import io.airbyte.api.client.generated.DestinationApi
import io.airbyte.api.client.generated.SourceApi
import io.airbyte.api.client.invoker.generated.ApiException
import io.airbyte.api.client.model.generated.*
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.Config
import java.util.*
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.Mockito

internal class ConnectorConfigUpdaterTest {
    private val mSourceApi: SourceApi = Mockito.mock(SourceApi::class.java)
    private val mDestinationApi: DestinationApi = Mockito.mock(DestinationApi::class.java)

    private var connectorConfigUpdater: ConnectorConfigUpdater? = null

    @BeforeEach
    @Throws(ApiException::class)
    fun setUp() {
        Mockito.`when`(mSourceApi.getSource(SourceIdRequestBody().sourceId(SOURCE_ID)))
            .thenReturn(SourceRead().sourceId(SOURCE_ID).name(SOURCE_NAME))

        Mockito.`when`(
                mDestinationApi.getDestination(
                    DestinationIdRequestBody().destinationId(DESTINATION_ID)
                )
            )
            .thenReturn(DestinationRead().destinationId(DESTINATION_ID).name(DESTINATION_NAME))

        connectorConfigUpdater = ConnectorConfigUpdater(mSourceApi, mDestinationApi)
    }

    @Test
    @Throws(ApiException::class)
    fun testPersistSourceConfig() {
        val newConfiguration = Config().withAdditionalProperty("key", "new_value")
        val configJson = Jsons.jsonNode(newConfiguration.additionalProperties)

        val expectedSourceUpdate =
            SourceUpdate().sourceId(SOURCE_ID).name(SOURCE_NAME).connectionConfiguration(configJson)

        Mockito.`when`(mSourceApi.updateSource(Mockito.any()))
            .thenReturn(SourceRead().connectionConfiguration(configJson))

        connectorConfigUpdater!!.updateSource(SOURCE_ID, newConfiguration)
        Mockito.verify(mSourceApi).updateSource(expectedSourceUpdate)
    }

    @Test
    @Throws(ApiException::class)
    fun testPersistDestinationConfig() {
        val newConfiguration = Config().withAdditionalProperty("key", "new_value")
        val configJson = Jsons.jsonNode(newConfiguration.additionalProperties)

        val expectedDestinationUpdate =
            DestinationUpdate()
                .destinationId(DESTINATION_ID)
                .name(DESTINATION_NAME)
                .connectionConfiguration(configJson)

        Mockito.`when`(mDestinationApi.updateDestination(Mockito.any()))
            .thenReturn(DestinationRead().connectionConfiguration(configJson))

        connectorConfigUpdater!!.updateDestination(DESTINATION_ID, newConfiguration)
        Mockito.verify(mDestinationApi).updateDestination(expectedDestinationUpdate)
    }

    companion object {
        private val SOURCE_ID: UUID = UUID.randomUUID()
        private const val SOURCE_NAME = "source-stripe"
        private val DESTINATION_ID: UUID = UUID.randomUUID()
        private const val DESTINATION_NAME = "destination-google-sheets"
    }
}
