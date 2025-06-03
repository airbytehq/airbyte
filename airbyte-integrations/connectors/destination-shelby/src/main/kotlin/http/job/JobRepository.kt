package io.airbyte.integrations.destination.shelby.http.job

import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.Dedupe
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.ImportType
import io.airbyte.cdk.load.command.SoftDelete
import io.airbyte.cdk.load.command.Update
import io.airbyte.cdk.load.http.HttpClient
import io.airbyte.cdk.load.http.Request
import io.airbyte.cdk.load.http.RequestMethod
import io.airbyte.cdk.load.http.Response
import io.airbyte.cdk.load.http.decoder.CsvDecoder
import io.airbyte.cdk.load.http.decoder.JsonDecoder
import io.airbyte.cdk.util.Jsons

private val TERMINAL_STATES: Set<String> = setOf("Aborted", "Failed", "JobComplete")
private val FAILED_STATES: Set<String> = setOf("Aborted", "Failed")

class JobRepository(httpClient: HttpClient, baseUrl: String) {
    private val httpClient: HttpClient = httpClient
    private val baseUrl: String = baseUrl
    private val jsonDecoder: JsonDecoder = JsonDecoder()
    private val csvDecoder: CsvDecoder = CsvDecoder()

    fun create(stream: DestinationStream, batch: Batch) : Job {
        val jobId: String = createSalesforceJob(stream)
        uploadBatch(jobId, batch)
        return Job(jobId)
    }

    fun startIngestion(job: Job) {
        val response: Response = httpClient.sendRequest(
            Request(
                method = RequestMethod.PATCH,
                url = "$baseUrl/services/data/v62.0/jobs/ingest/${job.id}",
                headers = mapOf("Content-Type" to "application/json"),
                body = "{\"state\": \"UploadComplete\"}".toByteArray(Charsets.UTF_8)
            )
        )
        if (response.statusCode != 200) {
            throw IllegalStateException("Invalid response with status code ${response.statusCode} while starting ingestion: ${jsonDecoder.decode(response).toPrettyString()}")
        }
        job.status = JobStatus.INGESTING
    }

    fun updateStatus(job: Job) {
        val response: Response = httpClient.sendRequest(
            Request(
                method = RequestMethod.GET,
                url = "$baseUrl/services/data/v62.0/jobs/ingest/${job.id}",
            )
        )

        if (response.statusCode != 200) {
            throw IllegalStateException("Invalid response with status code ${response.statusCode} while polling for job status: ${jsonDecoder.decode(response).toPrettyString()}")
        }

        val salesforceJobStatus: String = jsonDecoder.decode(response).get("state").asText()
        if (salesforceJobStatus in TERMINAL_STATES) {
            if (salesforceJobStatus in FAILED_STATES) {
                job.status = JobStatus.INCOMPLETE
            } else {
                job.status = JobStatus.COMPLETE
            }
        }
    }

    fun printFailedRecords(job: Job) {
        val response: Response = httpClient.sendRequest(
            Request(
                method = RequestMethod.GET,
                url = "$baseUrl/services/data/v62.0/jobs/ingest/${job.id}/failedResults",
            )
        )
        val decodedResponse = csvDecoder.decode(response)
        // FIXME we need to redact the record content for now if we decide to print it
        decodedResponse.forEach { print(it) }
    }

    private fun createSalesforceJob(stream: DestinationStream): String {
        val bodyNode: ObjectNode = Jsons.objectNode()
            .put("object", stream.destinationObjectName)
            .put("operation", assembleOperation(stream.importType))
        if (stream.importType is Update) {
            // for the externalIdFieldName, we get [0] here because we know the matchingKeys can't be composite for Salesforce
            bodyNode.put("externalIdFieldName", (stream.importType as Update).matchingKey[0])
        }
        val response: Response = httpClient.sendRequest(
            Request(
                method = RequestMethod.POST,
                url = "$baseUrl/services/data/v62.0/jobs/ingest",
                headers = mapOf("Content-Type" to "application/json"),
                body = bodyNode.toString().toByteArray(Charsets.UTF_8)
            )
        )
        if (response.statusCode != 200) {
            throw IllegalStateException("Invalid response with status code ${response.statusCode} while creating job: ${jsonDecoder.decode(response).toPrettyString()}")
        }

        return jsonDecoder.decode(response).get("id").asText()
    }

    private fun uploadBatch(jobId: String, batch: Batch) {
        val response: Response = httpClient.sendRequest(
            Request(
                method = RequestMethod.PUT,
                url = "$baseUrl/services/data/v62.0/jobs/ingest/$jobId/batches",
                headers = mapOf("Content-Type" to "text/csv"),
                body = batch.toRequestBody()
            )
        )

        if (response.statusCode != 201) {
            throw IllegalStateException("Invalid response with status code ${response.statusCode} while uploading batch: ${jsonDecoder.decode(response).toPrettyString()}")
        }
    }

    private fun assembleOperation(importType: ImportType): String {
        return when (importType) {
            is Append -> "insert"
            is Dedupe -> "upsert"
            is Update -> "update"
            is SoftDelete -> "delete"
             else -> throw IllegalArgumentException("Unsupported import type $importType")
        }
    }
}
