/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_data_lake

import io.airbyte.cdk.load.write.BasicPerformanceTest
import java.nio.file.Files
import org.junit.jupiter.api.Disabled

@Disabled("We don't want this to run in CI")
class GcsDataLakePerformanceTest :
    BasicPerformanceTest(
        configContents = Files.readString(GcsDataLakeTestUtil.GLUE_CONFIG_PATH),
        configSpecClass = GcsDataLakeSpecification::class.java,
        defaultRecordsToInsert = 500_000,
    )
