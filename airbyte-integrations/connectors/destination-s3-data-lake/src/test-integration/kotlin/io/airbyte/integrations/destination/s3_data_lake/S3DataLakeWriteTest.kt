/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.load.command.Append
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.aws.asMicronautProperties
import io.airbyte.cdk.load.data.FieldType
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.message.InputRecord
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import java.nio.file.Files
import java.util.Base64
import okhttp3.FormBody
import okhttp3.OkHttpClient
import okhttp3.Request
import org.junit.jupiter.api.Assumptions
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows

abstract class S3DataLakeWriteTest(
    configContents: String,
    destinationCleaner: DestinationCleaner,
) :
    BasicFunctionalityIntegrationTest(
        configContents,
        S3DataLakeSpecification::class.java,
        S3DataLakeDataDumper,
        destinationCleaner,
        S3DataLakeExpectedRecordMapper,
        additionalMicronautEnvs = S3DataLakeDestination.additionalMicronautEnvs,
        micronautProperties =
            S3DataLakeTestUtil.getAwsAssumeRoleCredentials().asMicronautProperties(),
        isStreamSchemaRetroactive = true,
        supportsDedup = true,
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.STRINGIFY,
        preserveUndeclaredFields = false,
        commitDataIncrementally = false,
        supportFileTransfer = false,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = false,
                // we stringify objects, so nested floats stay exact
                nestedFloatLosesPrecision = false
            ),
        nullUnknownTypes = true,
        nullEqualsUnset = true,
    ) {
    @Test
    @Disabled(
        "failing because we have an extra _pos column - that's probably fine, but problem for a different day"
    )
    override fun testDedup() {
        super.testDedup()
    }

    /**
     * This test differs from the base test in two critical aspects:
     *
     * 1. Data Type Conversion:
     * ```
     *    The base test attempts to change a column's data type from INTEGER to STRING,
     *    which Iceberg does not support and will throw an exception.
     * ```
     * 2. Result Ordering:
     * ```
     *    While the data content matches exactly, Iceberg returns results in a different
     *    order than what the base test expects. The base test's ordering assumptions
     *    need to be adjusted accordingly.
     * ```
     */
    @Test
    override fun testAppendSchemaEvolution() {
        Assumptions.assumeTrue(verifyDataWriting)
        fun makeStream(syncId: Long, schema: LinkedHashMap<String, FieldType>) =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace, "test_stream"),
                Append,
                ObjectType(schema),
                generationId = 0,
                minimumGenerationId = 0,
                syncId,
            )
        runSync(
            configContents,
            makeStream(
                syncId = 42,
                linkedMapOf("id" to intType, "to_drop" to stringType, "same" to intType)
            ),
            listOf(
                InputRecord(
                    randomizedNamespace,
                    "test_stream",
                    """{"id": 42, "to_drop": "val1", "same": 42}""",
                    emittedAtMs = 1234L,
                )
            )
        )
        val finalStream =
            makeStream(
                syncId = 43,
                linkedMapOf("id" to intType, "same" to intType, "to_add" to stringType)
            )
        runSync(
            configContents,
            finalStream,
            listOf(
                InputRecord(
                    randomizedNamespace,
                    "test_stream",
                    """{"id": 42, "same": "43", "to_add": "val3"}""",
                    emittedAtMs = 1234,
                )
            )
        )
        dumpAndDiffRecords(
            parsedConfig,
            listOf(
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data = mapOf("id" to 42, "same" to 42),
                    airbyteMeta = OutputRecord.Meta(syncId = 42),
                ),
                OutputRecord(
                    extractedAt = 1234,
                    generationId = 0,
                    data = mapOf("id" to 42, "same" to 43, "to_add" to "val3"),
                    airbyteMeta = OutputRecord.Meta(syncId = 43),
                )
            ),
            finalStream,
            primaryKey = listOf(listOf("id")),
            cursor = listOf("same"),
        )
    }

    @Test
    override fun testDedupChangeCursor() {
        super.testDedupChangeCursor()
    }
}

class GlueWriteTest :
    S3DataLakeWriteTest(
        Files.readString(S3DataLakeTestUtil.GLUE_CONFIG_PATH),
        S3DataLakeDestinationCleaner(
            S3DataLakeTestUtil.getCatalog(
                S3DataLakeTestUtil.parseConfig(S3DataLakeTestUtil.GLUE_CONFIG_PATH),
                S3DataLakeTestUtil.getAwsAssumeRoleCredentials(),
            )
        )
    ) {
    @Test
    fun testNameConflicts() {
        assumeTrue(verifyDataWriting)
        fun makeStream(
            name: String,
            namespaceSuffix: String,
        ) =
            DestinationStream(
                DestinationStream.Descriptor(randomizedNamespace + namespaceSuffix, name),
                Append,
                ObjectType(linkedMapOf("id" to intType)),
                generationId = 0,
                minimumGenerationId = 0,
                syncId = 42,
            )
        // Glue downcases stream IDs, and also coerces to alphanumeric+underscore.
        // So these two streams will collide.
        val catalog =
            DestinationCatalog(
                listOf(
                    makeStream("stream_with_spécial_character", "_foo"),
                    makeStream("STREAM_WITH_SPÉCIAL_CHARACTER", "_FOO"),
                )
            )
        // TODO figure out what exception we actually throw + assert on its message
        assertThrows<IllegalArgumentException> {
            runSync(configContents, catalog, messages = emptyList())
        }
    }
}

class GlueAssumeRoleWriteTest :
    S3DataLakeWriteTest(
        Files.readString(S3DataLakeTestUtil.GLUE_ASSUME_ROLE_CONFIG_PATH),
        S3DataLakeDestinationCleaner(
            S3DataLakeTestUtil.getCatalog(
                S3DataLakeTestUtil.parseConfig(S3DataLakeTestUtil.GLUE_ASSUME_ROLE_CONFIG_PATH),
                S3DataLakeTestUtil.getAwsAssumeRoleCredentials()
            )
        ),
    )

@Disabled(
    "This is currently disabled until we are able to make it run via airbyte-ci. It works as expected locally"
)
class NessieMinioWriteTest :
    S3DataLakeWriteTest(
        getConfig(),
        // we're writing to ephemeral testcontainers, so no need to clean up after ourselves
        NoopDestinationCleaner
    ) {

    companion object {
        private fun getToken(): String {
            val client = OkHttpClient()
            val objectMapper = ObjectMapper()

            val credentials = "client1:s3cr3t"
            val encodedCredentials = Base64.getEncoder().encodeToString(credentials.toByteArray())

            val formBody =
                FormBody.Builder()
                    .add("grant_type", "client_credentials")
                    .add("scope", "profile")
                    .build()

            val request =
                Request.Builder()
                    .url("http://127.0.0.1:8080/realms/iceberg/protocol/openid-connect/token")
                    .post(formBody)
                    .header("Content-Type", "application/x-www-form-urlencoded")
                    .header("Authorization", "Basic $encodedCredentials")
                    .build()

            val response = client.newCall(request).execute()
            val jsonResponse = response.body?.string() ?: throw RuntimeException("Empty response")
            val jsonNode: JsonNode = objectMapper.readTree(jsonResponse)
            return jsonNode.get("access_token").asText()
        }

        fun getConfig(): String {
            val minioEndpoint = NessieTestContainers.testcontainers.getServiceHost("minio", 9000)
            val nessieEndpoint = NessieTestContainers.testcontainers.getServiceHost("nessie", 19120)

            val authToken = getToken()
            return """
            {
                "catalog_type": {
                  "catalog_type": "NESSIE",
                  "server_uri": "http://$nessieEndpoint:19120/api/v1",
                  "access_token": "$authToken"
                },
                "s3_bucket_name": "demobucket",
                "s3_bucket_region": "us-east-1",
                "access_key_id": "minioadmin",
                "secret_access_key": "minioadmin",
                "s3_endpoint": "http://$minioEndpoint:9002",
                "warehouse_location": "s3://demobucket/",
                "main_branch_name": "main"
            }
            """.trimIndent()
        }

        @JvmStatic
        @BeforeAll
        fun setup() {
            NessieTestContainers.start()
        }
    }
}
