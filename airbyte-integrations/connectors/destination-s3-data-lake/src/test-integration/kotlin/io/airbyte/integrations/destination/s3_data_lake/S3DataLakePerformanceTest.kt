package io.airbyte.integrations.destination.s3_data_lake

import io.airbyte.cdk.load.command.aws.asMicronautProperties
import io.airbyte.cdk.load.write.BasicPerformanceTest
import java.nio.file.Files

class S3DataLakePerformanceTest :
    BasicPerformanceTest(
        configContents = Files.readString(S3DataLakeTestUtil.GLUE_CONFIG_PATH),
        configSpecClass = S3DataLakeSpecification::class.java,
        defaultRecordsToInsert = 500_000,
        micronautProperties = S3DataLakeTestUtil.getAwsAssumeRoleCredentials().asMicronautProperties(),
    )
