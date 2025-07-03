/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.customerio

import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.http.decoder.JsonDecoder
import io.airbyte.cdk.load.http.getBodyOrEmpty
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.load.message.StreamKey
import io.airbyte.cdk.load.util.serializeToJsonBytes
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.write.dlq.DlqLoader
import io.airbyte.cdk.util.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging

private val logger = KotlinLogging.logger {}

class CustomerIoState(private val httpClient: HttpClient) : AutoCloseable {

    companion object {
        val EXPECTED_PROPERTIES: Set<String> =
            setOf<String>(
                "person_email",
                "event_name",
                "event_id",
                "timestamp",
            )
    }

    val decoder: JsonDecoder = JsonDecoder()
    val requestBody: ObjectNode = Jsons.objectNode()
    val batch: ArrayNode = requestBody.putArray("batch")
    // In order to populate the rejected records list, we need to have the list of records in order
    // of which they are sent to Customer IO as Customer IO flags the errors by index
    val orderedRecords: MutableList<DestinationRecordRaw> = mutableListOf()

    fun accumulate(record: DestinationRecordRaw) {
        orderedRecords.add(record)
        batch.add(createBatchEntry(record))
    }

    fun isFull(): Boolean =
        requestBody.serializeToString().toByteArray(Charsets.UTF_8).size > 500_000

    fun flush(): List<DestinationRecordRaw>? {
        if (batch.isEmpty) {
            logger.info { "No records in batch hence the HTTP request will be performed" }
            return emptyList()
        }

        val response: Response =
            httpClient.send(
                Request(
                    method = RequestMethod.POST,
                    url = "https://track.customer.io/api/v2/batch",
                    headers = mapOf("Content-Type" to "application/json"),
                    body = requestBody.serializeToJsonBytes()
                )
            )

        response.use {
            return when (response.statusCode) {
                200 -> emptyList()
                207 ->
                    decoder.decode(response.getBodyOrEmpty()).get("errors").asIterable().map {
                        orderedRecords[it.get("batch_index").asInt()]
                    } // FIXME also add reason, field and message as part of meta
                else ->
                    throw IllegalStateException(
                        "Invalid response with status code ${response.statusCode} while starting ingestion: ${response.getBodyOrEmpty().reader(Charsets.UTF_8).readText()}"
                    )
            }
        }
    }

    override fun close() {}

    /**
     * In theory, there is a limit of 32 kb per batch entry but it is not yet validated here and we
     * will wait for this to affect customers to take action.
     */
    private fun createBatchEntry(record: DestinationRecordRaw): ObjectNode {
        val recordAsJson = record.asJsonRecord()
        val personEmail =
            recordAsJson.get("person_email")?.asText()
                ?: throw IllegalArgumentException("person_email field cannot be empty")
        val eventName =
            recordAsJson.get("event_name")?.asText()
                ?: throw IllegalArgumentException("event_name field cannot be empty")
        val batchEntry =
            Jsons.objectNode().put("type", "person").put("action", "event").put("name", eventName)

        batchEntry.putObject("identifiers").put("email", personEmail)

        recordAsJson.get("event_id")?.let { batchEntry.put("id", it.asText()) }
        recordAsJson.get("timestamp")?.let { batchEntry.put("timestamp", it.asText()) }

        val attributes = batchEntry.putObject("attributes")
        (recordAsJson as ObjectNode).fields().forEach { (key, value) ->
            if (key !in EXPECTED_PROPERTIES) {
                attributes.put(key, value.asText())
            }
        }

        return batchEntry
    }
}

class CustomerIoLoader(private val httpClient: HttpClient) : DlqLoader<CustomerIoState> {
    override fun start(key: StreamKey, part: Int): CustomerIoState {
        logger.info { "CustomerIoLoader.start for ${key.serializeToString()} with part $part" }

        return CustomerIoState(httpClient)
    }

    override fun accept(
        record: DestinationRecordRaw,
        state: CustomerIoState
    ): DlqLoader.DlqLoadResult {
        state.accumulate(record)
        if (state.isFull()) {
            val failedRecords = state.flush()
            return DlqLoader.Complete(failedRecords)
        } else {
            return DlqLoader.Incomplete
        }
    }

    override fun finish(state: CustomerIoState): DlqLoader.Complete =
        DlqLoader.Complete(state.flush())

    override fun close() {}
}
