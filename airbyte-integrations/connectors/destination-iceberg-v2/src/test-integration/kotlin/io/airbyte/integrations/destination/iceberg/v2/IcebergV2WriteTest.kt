/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.StronglyTyped
import java.util.Base64
import okhttp3.*
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test

abstract class IcebergV2WriteTest(configContents: String) :
    BasicFunctionalityIntegrationTest(
        configContents,
        IcebergV2Specification::class.java,
        IcebergV2DataDumper,
        NoopDestinationCleaner,
        NoopExpectedRecordMapper,
        // TODO let's validate these - I'm making some assumptions about how iceberg works
        isStreamSchemaRetroactive = true,
        supportsDedup = false,
        stringifySchemalessObjects = true,
        promoteUnionToObject = true,
        preserveUndeclaredFields = false,
        commitDataIncrementally = false,
        allTypesBehavior = StronglyTyped(),
    ) {
    companion object {
        @JvmStatic
        @BeforeAll
        fun setup() {
            NessieTestContainers.start()
        }
    }
}

class IcebergNessieMinioWriteTest : IcebergV2WriteTest(getConfig()) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }

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
            //            val minioPort =
            // NessieTestContainers.testcontainers.getServicePort("minio", 9000)

            val nessieEndpoint = NessieTestContainers.testcontainers.getServiceHost("nessie", 19120)
            //            val nessiePort =
            // NessieTestContainers.testcontainers.getServicePort("nessie", 19120)

            val authToken = getToken()
            return """
            {
                "s3_bucket_name": "demobucket",
                "s3_bucket_region": "us-east-1",
                "access_key_id": "minioadmin",
                "secret_access_key": "minioadmin",
                "s3_endpoint": "http://$minioEndpoint:9002",
                "server_uri": "http://$nessieEndpoint:19120/api/v1",
                "warehouse_location": "s3://demobucket/",
                "main_branch_name": "main",
                "access_token": "$authToken"
            }
            """.trimIndent()
        }
    }
}
