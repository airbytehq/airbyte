/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
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
    val records: MutableList<DestinationRecordRaw> = mutableListOf()

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
                data.properties().forEach { (key, value) -> properties.replace(key, value) }
            }
        batch.add(input)
        records.add(record)
    }

    fun isFull(): Boolean = batch.size() >= 100

    fun flush(): List<DestinationRecordRaw>? {
        logger.info { "Flushing batch of ${batch.size()} records" }
        if (batch.size() == 0) {
            return null
        }

        val inputs = (0 until batch.size()).map { batch.get(it) }
        val rejectedRecords = sendWithSplitRetry(inputs, records.toList())

        return rejectedRecords.ifEmpty { null }
    }

    /**
     * Sends a batch upsert request to HubSpot. On a 409 Conflict response, the batch is split in
     * half and each half is retried recursively. This isolates the problematic record(s) that cause
     * the conflict while allowing the unaffected records to be loaded successfully.
     *
     * When a single-record batch still results in a 409, that record is the root cause of the
     * conflict and is returned as a rejected record for the dead letter queue.
     */
    internal fun sendWithSplitRetry(
        inputs: List<JsonNode>,
        associatedRecords: List<DestinationRecordRaw>
    ): List<DestinationRecordRaw> {
        val batchRequestBody = Jsons.objectNode()
        val batchInputs = batchRequestBody.putArray("inputs")
        inputs.forEach { batchInputs.add(it) }

        val url =
            "https://api.hubapi.com/crm/v3/objects/${objectDao.fetchObjectTypeId(stream.destinationObjectName ?: throw IllegalStateException("destinationObjectName required"))}/batch/upsert"

        val response: Response =
            httpClient.send(
                Request(
                    method = RequestMethod.POST,
                    url = url,
                    headers = mapOf("Content-Type" to "application/json"),
                    body = batchRequestBody.serializeToJsonBytes()
                )
            )

        response.use {
            return when (response.statusCode) {
                200 -> emptyList()
                207 -> emptyList() // FIXME generate dlq record with error from hubspot
                409 -> {
                    val responseBody = response.getBodyOrEmpty().reader(Charsets.UTF_8).readText()

                    if (inputs.size == 1) {
                        logger.warn {
                            "HubSpot returned 409 Conflict for a single record. " +
                                "Routing to rejected records. Response: $responseBody"
                        }
                        return associatedRecords
                    }

                    logger.info {
                        "HubSpot returned 409 Conflict for batch of ${inputs.size} records. " +
                            "Splitting batch and retrying each half. Response: $responseBody"
                    }

                    val mid = inputs.size / 2
                    val firstHalfInputs = inputs.subList(0, mid)
                    val secondHalfInputs = inputs.subList(mid, inputs.size)
                    val firstHalfRecords = associatedRecords.subList(0, mid)
                    val secondHalfRecords = associatedRecords.subList(mid, associatedRecords.size)

                    val rejectedFromFirst = sendWithSplitRetry(firstHalfInputs, firstHalfRecords)
                    val rejectedFromSecond = sendWithSplitRetry(secondHalfInputs, secondHalfRecords)

                    rejectedFromFirst + rejectedFromSecond
                }
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
