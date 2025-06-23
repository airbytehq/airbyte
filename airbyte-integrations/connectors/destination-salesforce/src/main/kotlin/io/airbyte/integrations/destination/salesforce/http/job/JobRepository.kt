/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.salesforce.io.airbyte.integrations.destination.salesforce.http.job

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.file.csv.CsvDecoder
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.http.consumeBodyToString
import io.airbyte.cdk.load.http.decoder.JsonDecoder
import io.airbyte.cdk.load.http.getBodyOrEmpty
import io.airbyte.cdk.util.Jsons
import jakarta.inject.Singleton
import java.util.function.Supplier

private val TERMINAL_STATES: Set<String> = setOf("Aborted", "Failed", "JobComplete")
private val FAILED_STATES: Set<String> = setOf("Aborted", "Failed")

private const val SALESFORCE_INSERT_OPERATION = "insert"
private const val SALESFORCE_UPDATE_OPERATION = "update"
private const val SALESFORCE_UPSERT_OPERATION = "upsert"
private const val SALESFORCE_SOFT_DELETE_OPERATION = "delete"

@Singleton
class JobRepository(private val httpClient: HttpClient, private val baseUrl: Supplier<String>) {
    private val jsonDecoder: JsonDecoder = JsonDecoder()
    private val csvDecoder: CsvDecoder = CsvDecoder()

    fun create(stream: DestinationStream, batch: ByteArray): Job {
        val jobId: String = createSalesforceJob(stream)
        uploadBatch(jobId, batch)
        return Job(jobId)
    }

    fun startIngestion(job: Job) {
        val response: Response =
            httpClient.send(
                Request(
                    method = RequestMethod.PATCH,
                    url = "${baseUrl.get()}/services/data/v62.0/jobs/ingest/${job.id}",
                    headers = mapOf("Content-Type" to "application/json"),
                    body = "{\"state\": \"UploadComplete\"}".toByteArray(Charsets.UTF_8)
                )
            )
        if (response.statusCode != 200) {
            throw IllegalStateException(
                "Invalid response with status code ${response.statusCode} while starting ingestion: ${response.consumeBodyToString()}"
            )
        }
        job.status = JobStatus.INGESTING
    }

    fun updateStatus(job: Job) {
        val response: Response =
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url = "${baseUrl.get()}/services/data/v62.0/jobs/ingest/${job.id}",
                )
            )

        if (response.statusCode != 200) {
            throw IllegalStateException(
                "Invalid response with status code ${response.statusCode} while polling for job status: ${response.consumeBodyToString()}"
            )
        }

        val ingestJobBody: JsonNode = response.use { jsonDecoder.decode(it.getBodyOrEmpty()) }
        val jobStatus =
            ingestJobBody.get("state")?.asText()
                ?: throw IllegalStateException(
                    "Response expect a state but got {${ingestJobBody.toPrettyString()}"
                )
        if (jobStatus in TERMINAL_STATES) {
            if (jobStatus in FAILED_STATES) {
                job.status = JobStatus.INCOMPLETE
            } else {
                job.status = JobStatus.COMPLETE
            }
        }
    }

    fun fetchFailedRecords(job: Job): List<JsonNode> {
        val response: Response =
            httpClient.send(
                Request(
                    method = RequestMethod.GET,
                    url =
                        "${baseUrl.get()}/services/data/v62.0/jobs/ingest/${job.id}/failedResults",
                )
            )
        return response.use { csvDecoder.decode(response.getBodyOrEmpty()).toList() }
    }

    private fun createSalesforceJob(stream: DestinationStream): String {
        val bodyNode: ObjectNode =
            Jsons.objectNode()
                .put("object", stream.destinationObjectName)
                .put("operation", assembleOperation(stream.importType))
        if (stream.importType is Dedupe) {
            val matchingKey = stream.matchingKey ?: emptyList<String>()
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
            bodyNode.put("externalIdFieldName", matchingKey[0])
        }
        val response: Response =
            httpClient.send(
                Request(
                    method = RequestMethod.POST,
                    url = "${baseUrl.get()}/services/data/v62.0/jobs/ingest",
                    headers = mapOf("Content-Type" to "application/json"),
                    body = bodyNode.toString().toByteArray(Charsets.UTF_8)
                )
            )
        if (response.statusCode != 200) {
            throw IllegalStateException(
                "Invalid response with status code ${response.statusCode} while creating job: ${response.consumeBodyToString()}"
            )
        }

        val ingestJobBody: JsonNode = response.use { jsonDecoder.decode(it.getBodyOrEmpty()) }
        return ingestJobBody.get("id")?.asText()
            ?: throw IllegalStateException(
                "Response expect a id but got {${ingestJobBody.toPrettyString()}"
            )
    }

    private fun uploadBatch(jobId: String, batch: ByteArray) {
        val response: Response =
            httpClient.send(
                Request(
                    method = RequestMethod.PUT,
                    url = "${baseUrl.get()}/services/data/v62.0/jobs/ingest/$jobId/batches",
                    headers = mapOf("Content-Type" to "text/csv"),
                    body = batch
                )
            )

        if (response.statusCode != 201) {
            throw IllegalStateException(
                "Invalid response with status code ${response.statusCode} while uploading batch: ${response.consumeBodyToString()}"
            )
        }
    }

    private fun assembleOperation(importType: ImportType): String {
        return when (importType) {
            is Append -> SALESFORCE_INSERT_OPERATION
            is Dedupe -> SALESFORCE_UPSERT_OPERATION
            is Update -> SALESFORCE_UPDATE_OPERATION
            is SoftDelete -> SALESFORCE_SOFT_DELETE_OPERATION
            else -> throw IllegalArgumentException("Unsupported import type $importType")
        }
    }
}
