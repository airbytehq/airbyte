/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.write.BasicPerformanceTest
import org.junit.jupiter.api.Disabled

/** Performance test (opt-in, disabled in CI). */
@Disabled("We don't want this to run in CI")
class GcsV2AvroSnappyPerformanceTest :
    BasicPerformanceTest(
        configContents = GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.AVRO_SNAPPY_FORMAT),
        configSpecClass = GcsV2Specification::class.java,
        defaultRecordsToInsert = 1_000_000,
    )

/** Performance test in socket mode (opt-in, disabled in CI). */
@Disabled("We don't want this to run in CI")
class GcsV2AvroSnappyPerformanceTestSockets :
    BasicPerformanceTest(
        configContents = GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.AVRO_SNAPPY_FORMAT),
        configSpecClass = GcsV2Specification::class.java,
        defaultRecordsToInsert = 1_000_000,
        dataChannelMedium = DataChannelMedium.SOCKET,
    )
