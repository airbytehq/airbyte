/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.write.BasicPerformanceTest
import org.junit.jupiter.api.Disabled

/**
 * Mirror of S3V2PerformanceTest, minus everything AWS-specific.
 *
 * Unlike S3, GCS auth is HMAC-only: there is no assume-role, so there are no performance-test
 * micronaut properties to pass. [BasicPerformanceTest.micronautProperties] therefore defaults to
 * `emptyMap()`.
 *
 * These are opt-in only ([Disabled]), exactly like the S3 performance tests, so they never run in
 * CI.
 */
@Disabled("We don't want this to run in CI")
class GcsV2AvroSnappyPerformanceTest :
    BasicPerformanceTest(
        configContents = GcsV2TestUtils.getConfig(GcsV2TestUtils.AVRO_SNAPPY_CONFIG_PATH),
        configSpecClass = GcsV2Specification::class.java,
        defaultRecordsToInsert = 1_000_000,
    )

/**
 * Performance tests in socket mode are of limited utility, as the non-docker harness is slow, and
 * the ceiling on local networks is often lower than the theoretical max. For now this is mostly
 * just an opt-in local e2e sanity check.
 *
 * Note: Performance tests can't support protobuf until we do something about the manual munging of
 * records.
 */
@Disabled("We don't want this to run in CI")
class GcsV2AvroSnappyPerformanceTestSockets :
    BasicPerformanceTest(
        configContents = GcsV2TestUtils.getConfig(GcsV2TestUtils.AVRO_SNAPPY_CONFIG_PATH),
        configSpecClass = GcsV2Specification::class.java,
        defaultRecordsToInsert = 1_000_000,
        dataChannelMedium = DataChannelMedium.SOCKET,
    )
