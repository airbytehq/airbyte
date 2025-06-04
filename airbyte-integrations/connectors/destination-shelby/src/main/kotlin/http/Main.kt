/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.shelby.http

import dev.failsafe.RetryPolicy
import io.airbyte.cdk.load.command.DestinationStreamFactory
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.json.JsonSchemaToAirbyteType
import io.airbyte.cdk.load.http.authentication.OAuthAuthenticator
import io.airbyte.cdk.load.http.okhttp.AirbyteOkHttpClient
import io.airbyte.cdk.load.message.DestinationRecordRaw
import io.airbyte.cdk.util.Jsons
import io.airbyte.integrations.destination.shelby.http.discover.SalesforceOperationRepository
import io.airbyte.integrations.destination.shelby.http.job.Job
import io.airbyte.integrations.destination.shelby.http.job.JobRepository
import io.airbyte.integrations.destination.shelby.http.job.Batch
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import io.airbyte.protocol.models.v0.AirbyteStream
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import io.airbyte.protocol.models.v0.DestinationSyncMode
import okhttp3.OkHttpClient


val clientId: String = "<redacted>"
val clientSecret: String = "<redacted>"
val refreshToken: String = "<redacted>"

val isSandbox: Boolean = true

private const val STREAM_NAME = "test_stream"
private const val SCHEMA =
    """
        {
            "type": "object",
            "properties": {
                "Name": {
                    "type": "string"
                },
                "Clearbit_Account_Indexed_At__c": {
                    "type": "string",
                    "format": "date-time",
                    "airbyte_type": "timestamp_with_timezone"
                }
            }
        }
    """

fun main() {
    val authEndpoint: String = "https://${if (isSandbox) "test" else "login"}.salesforce.com/services/oauth2/token"
    val authenticator: OAuthAuthenticator = OAuthAuthenticator(authEndpoint, clientId, clientSecret, refreshToken)
    val baseUrl: String = authenticator.queryForAccessToken().get("instance_url").asText()

    val okhttpClient: OkHttpClient = OkHttpClient.Builder().addInterceptor(authenticator).build()
    val httpClient = AirbyteOkHttpClient(okhttpClient, RetryPolicy.ofDefaults())
//    testDiscover(httpClient, baseUrl)
    testWrite(httpClient, baseUrl)
    println("DONE")
}

private fun testWrite(httpClient: AirbyteOkHttpClient, baseUrl: String) {
    val properties = linkedMapOf("Name" to FieldType(StringType, false), "Clearbit_Account_Indexed_At__c" to FieldType(StringType, false))
    val batch: Batch = Batch(ObjectType(properties))
    val destinationStream = createDestinationStream()
    batch.add(
        DestinationRecordRaw(
            destinationStream,
            AirbyteMessage()
                .withType(AirbyteMessage.Type.RECORD)
                .withRecord(
                    AirbyteRecordMessage()
                        .withStream(STREAM_NAME)
                        .withData(Jsons.objectNode().put("Name", "kotlin code test").put("Clearbit_Account_Indexed_At__c", "a date"))
                        .withEmittedAt(0),
                ),
            ObjectType(properties),
            -1L,
        ),
    )
    val jobRepository: JobRepository = JobRepository(httpClient, baseUrl)
    val job: Job = jobRepository.create(destinationStream, batch)
    jobRepository.startIngestion(job)
    while (true) {
        jobRepository.updateStatus(job)
        if (job.status.isTerminal()) {
            break
        }
        Thread.sleep(5000)
    }
    jobRepository.printFailedRecords(job)
}

private fun testDiscover(httpClient: AirbyteOkHttpClient, baseUrl: String) {
    val operations = SalesforceOperationRepository(httpClient, baseUrl).fetchAll()
    println(operations)
}

private fun createDestinationStream() = DestinationStreamFactory(
    JsonSchemaToAirbyteType(JsonSchemaToAirbyteType.UnionBehavior.DEFAULT),
).make(
    ConfiguredAirbyteStream()
        .withStream(
            AirbyteStream().withName(STREAM_NAME).withJsonSchema(Jsons.readTree(SCHEMA)),
        )
        .withDestinationObjectName("Account")
        .withDestinationSyncMode(DestinationSyncMode.APPEND)
        .withSyncId(12)
        .withMinimumGenerationId(34)
        .withGenerationId(56)
        .withIncludeFiles(false)
)
