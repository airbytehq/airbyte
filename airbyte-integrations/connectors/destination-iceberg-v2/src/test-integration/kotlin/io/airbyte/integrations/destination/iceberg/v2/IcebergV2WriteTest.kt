/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.iceberg.v2

import io.airbyte.cdk.load.test.util.FakeDataDumper
import io.airbyte.cdk.load.test.util.NoopDestinationCleaner
import io.airbyte.cdk.load.test.util.NoopExpectedRecordMapper
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.integrations.destination.iceberg.v2.IcebergV2TestUtil.PATH
import java.io.File
import java.nio.file.Files
import java.nio.file.Path
import org.junit.ClassRule
import org.junit.jupiter.api.AfterAll
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.Test
import org.testcontainers.containers.DockerComposeContainer


abstract class IcebergV2WriteTest(configContents: String) :
    BasicFunctionalityIntegrationTest(
        configContents,
        IcebergV2Specification::class.java,
        FakeDataDumper,
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

class IcebergNessieMinioWriteTest : IcebergV2WriteTest(config) {
    companion object {
        // TODO we need to inject the service host/port into this config
        //   i.e. testcontainers.getServiceHost / testcontainers.getServicePort
        //   ... so this probably should be a function getConfig()
        val config = """
            {
              "s3_bucket_name": "test_bucket",
              "s3_bucket_region": "us-east-1",
              "server_uri": "localhost",
              "warehouse_location": "foo",
              "main_branch_name": "main"
            }
        """.trimIndent()
    }
}
