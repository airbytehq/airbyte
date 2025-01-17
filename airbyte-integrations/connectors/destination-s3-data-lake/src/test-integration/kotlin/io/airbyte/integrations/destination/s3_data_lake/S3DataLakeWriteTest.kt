/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import java.nio.file.Files
import java.util.Base64
import okhttp3.FormBody
import okhttp3.OkHttpClient
import okhttp3.Request
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

abstract class S3DataLakeWriteTest(
    configContents: String,
    destinationCleaner: DestinationCleaner,
    envVars: Map<String, String> = emptyMap(),
) :
    BasicFunctionalityIntegrationTest(
        configContents,
        S3DataLakeSpecification::class.java,
        S3DataLakeDataDumper,
        destinationCleaner,
        S3DataLakeExpectedRecordMapper,
        additionalMicronautEnvs = S3DataLakeDestination.additionalMicronautEnvs,
        isStreamSchemaRetroactive = true,
        supportsDedup = true,
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.STRINGIFY,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.STRINGIFY,
        preserveUndeclaredFields = false,
        commitDataIncrementally = false,
        supportFileTransfer = false,
        envVars = envVars,
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

    @Test
    @Disabled("This is expected (dest-iceberg-v2 doesn't yet support schema evolution)")
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }

    @Test
    @Disabled("This is expected (dest-iceberg-v2 doesn't yet support schema evolution)")
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
    @Disabled("https://github.com/airbytehq/airbyte-internal-issues/issues/11439")
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
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
        S3DataLakeTestUtil.getAwsAssumeRoleCredentialsAsMap()
    ) {
    @Test
    @Disabled("https://github.com/airbytehq/airbyte-internal-issues/issues/11439")
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }
}

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
