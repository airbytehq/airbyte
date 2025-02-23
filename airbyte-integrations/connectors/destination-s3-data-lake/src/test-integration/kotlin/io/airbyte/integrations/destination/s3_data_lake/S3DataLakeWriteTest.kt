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
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.icerberg.parquet.IcebergDestinationCleaner
import io.airbyte.cdk.load.data.icerberg.parquet.IcebergWriteTest
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.toolkits.iceberg.parquet.SimpleTableIdGenerator
import io.airbyte.cdk.load.toolkits.iceberg.parquet.TableIdGenerator
import java.nio.file.Files
import java.util.Base64
import kotlin.test.assertContains
import okhttp3.FormBody
import okhttp3.OkHttpClient
import okhttp3.Request
import org.junit.jupiter.api.Assumptions.assumeTrue
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.parallel.Execution
import org.junit.jupiter.api.parallel.ExecutionMode

abstract class S3DataLakeWriteTest(
    configContents: String,
    destinationCleaner: DestinationCleaner,
    tableIdGenerator: TableIdGenerator,
) :
    IcebergWriteTest(
        configContents,
        S3DataLakeSpecification::class.java,
        { spec ->
            S3DataLakeTestUtil.getCatalog(
                S3DataLakeTestUtil.getConfig(spec),
                S3DataLakeTestUtil.getAwsAssumeRoleCredentials(),
            )
        },
        destinationCleaner,
        tableIdGenerator,
        additionalMicronautEnvs = S3DataLakeDestination.additionalMicronautEnvs,
        micronautProperties =
            S3DataLakeTestUtil.getAwsAssumeRoleCredentials().asMicronautProperties(),
    )

class GlueWriteTest :
    S3DataLakeWriteTest(
        Files.readString(S3DataLakeTestUtil.GLUE_CONFIG_PATH),
        IcebergDestinationCleaner(
            S3DataLakeTestUtil.getCatalog(
                S3DataLakeTestUtil.parseConfig(S3DataLakeTestUtil.GLUE_CONFIG_PATH),
                S3DataLakeTestUtil.getAwsAssumeRoleCredentials(),
            )
        ),
        GlueTableIdGenerator(null),
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

        val failure = expectFailure { runSync(updatedConfig, catalog, messages = emptyList()) }
        assertContains(failure.message, "Detected naming conflicts between streams")
    }
}

class GlueAssumeRoleWriteTest :
    S3DataLakeWriteTest(
        Files.readString(S3DataLakeTestUtil.GLUE_ASSUME_ROLE_CONFIG_PATH),
        IcebergDestinationCleaner(
            S3DataLakeTestUtil.getCatalog(
                S3DataLakeTestUtil.parseConfig(S3DataLakeTestUtil.GLUE_ASSUME_ROLE_CONFIG_PATH),
                S3DataLakeTestUtil.getAwsAssumeRoleCredentials()
            )
        ),
        GlueTableIdGenerator(null),
    )

class NessieMinioWriteTest :
    S3DataLakeWriteTest(
        getConfig(),
        // we're writing to ephemeral testcontainers, so no need to clean up after ourselves
        NoopDestinationCleaner,
        SimpleTableIdGenerator(),
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
                  "access_token": "$authToken",
                  "namespace": "<DEFAULT_NAMESPACE_PLACEHOLDER>"
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

// the basic REST catalog behaves poorly with multithreading,
// even across multiple streams.
// so run singlethreaded.
@Execution(ExecutionMode.SAME_THREAD)
class RestWriteTest :
    S3DataLakeWriteTest(getConfig(), NoopDestinationCleaner, SimpleTableIdGenerator()) {

    @Test
    @Disabled("https://github.com/airbytehq/airbyte-internal-issues/issues/11439")
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }

    override val manyStreamCount = 5

    @Disabled("This doesn't seem to work with concurrency, etc.")
    @Test
    override fun testManyStreamsCompletion() {
        super.testManyStreamsCompletion()
    }

    companion object {

        fun getConfig(): String {
            // We retrieve the ephemeral host/port from the updated RestTestContainers
            val minioEndpoint = RestTestContainers.testcontainers.getServiceHost("minio", 9000)
            val restEndpoint = RestTestContainers.testcontainers.getServiceHost("rest", 8181)

            return """
            {
                "catalog_type": {
                  "catalog_type": "REST",
                  "server_uri": "http://$restEndpoint:8181",
                  "namespace": "<DEFAULT_NAMESPACE_PLACEHOLDER>"
                },
                "s3_bucket_name": "warehouse",
                "s3_bucket_region": "us-east-1",
                "access_key_id": "admin",
                "secret_access_key": "password",
                "s3_endpoint": "http://$minioEndpoint:9100",
                "warehouse_location": "s3://warehouse/",
                "main_branch_name": "main"
            }
            """.trimIndent()
        }

        @JvmStatic
        @BeforeAll
        fun setup() {
            // Start the testcontainers environment once before any tests run
            RestTestContainers.start()
        }
    }
}
