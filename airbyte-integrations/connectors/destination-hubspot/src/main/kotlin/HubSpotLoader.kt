/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.hubspot

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.discoverer.operation.extract
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.http.decoder.JsonDecoder
import io.airbyte.cdk.load.http.getBodyOrEmpty
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.cdk.load.write.dlq.DlqLoader
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.hubspot.io.airbyte.integrations.destination.hubspot.http.HubSpotObjectTypeIdMapper
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

class HubSpotState(
    private val httpClient: HttpClient,
    private val objectDao: HubSpotObjectTypeIdMapper,
    private val stream: DestinationStream
) : AutoCloseable {
    val requestBody: ObjectNode = Jsons.objectNode()
    val batch: ArrayNode = requestBody.putArray("inputs")
    val decoder: JsonDecoder = JsonDecoder()

    fun accumulate(record: DestinationRecordRaw) {
        if (isFull()) {
            throw IllegalStateException("Can't add records as the batch is already full")
        }

        val data: JsonNode = record.asJsonRecord()
        val input =
            Jsons.objectNode().put("idProperty", getNonNestedMatchingKey()).apply {
                this.replace(
                    "id",
                    data.extract(
                        stream.matchingKey ?: throw IllegalStateException("Missing matching key")
                    )
                )
                val properties = this.putObject("properties")
                data.fields().forEach { (key, value) -> properties.replace(key, value) }
            }
        batch.add(input)
    }

    fun isFull(): Boolean = batch.size() >= 100

    fun flush(): List<DestinationRecordRaw>? {
        logger.info { "Flushing data" }
        val response: Response =
            httpClient.send(
                Request(
                    method = RequestMethod.POST,
                    // Note that knowing all the standard object names could improve performance of
                    // one HTTP request in the case the user does not sync custom objects so this
                    // could be optimized.
                    url =
                        "https://api.hubapi.com/crm/v3/objects/${objectDao.fetchObjectTypeId(stream.destinationObjectName ?: throw IllegalStateException("destinationObjectName required"))}/batch/upsert",
                    headers = mapOf("Content-Type" to "application/json"),
                    body = requestBody.serializeToJsonBytes()
                )
            )

        response.use {
            return when (response.statusCode) {
                200 -> null
                207 -> null // FIXME generate dlq record with error from hubspot
                else ->
                    throw IllegalStateException(
                        "Invalid response with status code ${response.statusCode} while starting ingestion: ${response.getBodyOrEmpty().reader(Charsets.UTF_8).readText()}"
                    )
            }
        }
    }

    override fun close() {}

    private fun getNonNestedMatchingKey(): String {
        val matchingKey = stream.matchingKey ?: emptyList()
        if (matchingKey.isEmpty()) {
            throw IllegalStateException(
                "In order to perform upserts, a matching key needs to be provided"
            )
        }
        if (matchingKey.size != 1) {
            throw IllegalStateException(
                "Matching keys for Salesforce need to have only one field but got $matchingKey"
            )
        }
        return matchingKey.get(0)
    }
}

class HubSpotLoader(
    private val httpClient: HttpClient,
    private val objectDao: HubSpotObjectTypeIdMapper,
    private val catalog: DestinationCatalog
) : DlqLoader<HubSpotState> {
    override fun start(key: StreamKey, part: Int): HubSpotState {
        return HubSpotState(
            httpClient,
            objectDao,
            catalog.streams.find { it.mappedDescriptor == key.stream }
                ?: throw IllegalStateException(
                    "Could not find stream ${key.stream} as part of the catalog."
                ),
        )
    }

    override fun accept(
        record: DestinationRecordRaw,
        state: HubSpotState
    ): DlqLoader.DlqLoadResult {
        state.accumulate(record)
        if (state.isFull()) {
            val failedRecords = state.flush()
            return DlqLoader.Complete(failedRecords)
        } else {
            return DlqLoader.Incomplete
        }
    }

    override fun finish(state: HubSpotState): DlqLoader.Complete = DlqLoader.Complete(state.flush())

    override fun close() {}
}
