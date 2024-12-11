/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.StronglyTyped
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
        fun getConfig(): String {
            val minioEndpoint = NessieTestContainers.testcontainers.getServiceHost("minio", 9000)
            //            val minioPort =
            // NessieTestContainers.testcontainers.getServicePort("minio", 9000)

            val nessieEndpoint = NessieTestContainers.testcontainers.getServiceHost("nessie", 19120)
            //            val nessiePort =
            // NessieTestContainers.testcontainers.getServicePort("nessie", 19120)

            return """
            {
                "s3_bucket_name": "demobucket",
                "s3_bucket_region": "us-east-1",
                "access_key_id": "minioadmin",
                "secret_access_key": "minioadmin",
                "s3_endpoint": "http://$minioEndpoint:9002",
                "server_uri": "http://$nessieEndpoint:19120/api/v1",
                "warehouse_location": "s3://demobucket/",
                "main_branch_name": "main"
            }
            """.trimIndent()
        }
    }
}
