/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.aws.asMicronautProperties
import io.airbyte.cdk.load.write.BasicPerformanceTest
import java.nio.file.Files
import org.junit.jupiter.api.Disabled

@Disabled("We don't want this to run in CI")
class S3DataLakePerformanceTest :
    BasicPerformanceTest(
        configContents = Files.readString(S3DataLakeTestUtil.GLUE_CONFIG_PATH),
        configSpecClass = S3DataLakeSpecification::class.java,
        defaultRecordsToInsert = 1_000_000,
        micronautProperties =
            S3DataLakeTestUtil.getAwsAssumeRoleCredentials().asMicronautProperties(),
    )
