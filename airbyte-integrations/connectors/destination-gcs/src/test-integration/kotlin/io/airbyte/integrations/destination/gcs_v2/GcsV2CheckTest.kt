/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.gcs_v2

import com.fasterxml.jackson.databind.ObjectMapper
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.command.FeatureFlag
import io.airbyte.cdk.load.check.CheckIntegrationTest
import io.airbyte.cdk.load.check.CheckTestConfig
import java.util.concurrent.TimeUnit
import java.util.regex.Pattern
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.Timeout

/**
 * Validates the `check` operation for the GCS v2 destination.
 *
 * Success configs verify that valid credentials + every supported output format pass the check.
 * Failure configs mirror the old v0.4.x acceptance tests (GcsDestinationAcceptanceTest):
 * - wrong HMAC key access ID
 * - wrong HMAC key secret
 * - non-existent bucket name
 *
 * All configs are built from the single `secrets/config.json` base with format injected in-memory.
 */
class GcsV2CheckTest :
    CheckIntegrationTest<GcsV2Specification>(
        successConfigFilenames =
            listOf(
                CheckTestConfig(
                    GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.AVRO_UNCOMPRESSED_FORMAT),
                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                    name = "avro-uncompressed",
                ),
                CheckTestConfig(
                    GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.AVRO_SNAPPY_FORMAT),
                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                    name = "avro-snappy",
                ),
                CheckTestConfig(
                    GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.JSONL_FORMAT),
                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                    name = "jsonl",
                ),
                CheckTestConfig(
                    GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.JSONL_UNCOMPRESSED_FORMAT),
                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                    name = "jsonl-uncompressed",
                ),
                CheckTestConfig(
                    GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.CSV_FORMAT),
                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                    name = "csv",
                ),
                CheckTestConfig(
                    GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.CSV_UNCOMPRESSED_FORMAT),
                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                    name = "csv-uncompressed",
                ),
                CheckTestConfig(
                    GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.PARQUET_SNAPPY_FORMAT),
                    setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                    name = "parquet-snappy",
                ),
            ),
        failConfigFilenamesAndFailureReasons = buildFailConfigs(),
        additionalMicronautEnvs = GcsV2Destination.additionalMicronautEnvs,
    ) {
    @Test
    @Timeout(5, unit = TimeUnit.MINUTES)
    override fun testSuccessConfigs() {
        super.testSuccessConfigs()
    }

    @Test
    @Timeout(5, unit = TimeUnit.MINUTES)
    override fun testFailConfigs() {
        super.testFailConfigs()
    }

    companion object {
        private val mapper = ObjectMapper()

        /**
         * Builds failure check configs by mutating a valid config with bad credentials or a
         * non-existent bucket. Mirrors the old v0.4.x GcsDestinationAcceptanceTest negative check
         * tests:
         * - testCheckIncorrectHmacKeyAccessIdCredential
         * - testCheckIncorrectHmacKeySecretCredential
         * - testCheckIncorrectBucketCredential
         *
         * The regex patterns are intentionally broad to accommodate differences in error messages
         * between AWS SDK versions and the GCS S3-interop endpoint.
         */
        private fun buildFailConfigs(): Map<CheckTestConfig, Pattern> {
            val baseConfig = GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.JSONL_FORMAT)
            return mapOf(
                // Wrong HMAC key access ID -> GCS returns InvalidAccessKeyId or
                // SignatureDoesNotMatch
                CheckTestConfig(
                    configContents =
                        mutateCredentialField(
                            baseConfig,
                            "hmac_key_access_id",
                            "fake-hmac-key-id",
                        ),
                    featureFlags = setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                    name = "incorrect-hmac-key-access-id",
                ) to
                    Pattern.compile(
                        "(?i)(InvalidAccessKeyId|SignatureDoesNotMatch|403|Forbidden|Access.?Denied)",
                    ),
                // Wrong HMAC key secret -> GCS returns SignatureDoesNotMatch
                CheckTestConfig(
                    configContents =
                        mutateCredentialField(
                            baseConfig,
                            "hmac_key_secret",
                            "fake-hmac-key-secret-40chars-padding!!",
                        ),
                    featureFlags = setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                    name = "incorrect-hmac-key-secret",
                ) to
                    Pattern.compile(
                        "(?i)(SignatureDoesNotMatch|403|Forbidden|Access.?Denied)",
                    ),
                // Non-existent bucket -> GCS returns NoSuchBucket or 404
                CheckTestConfig(
                    configContents =
                        mutateTopLevelField(
                            baseConfig,
                            "gcs_bucket_name",
                            "nonexistent-fake-bucket-xyz-12345",
                        ),
                    featureFlags = setOf(FeatureFlag.AIRBYTE_CLOUD_DEPLOYMENT),
                    name = "incorrect-bucket-name",
                ) to
                    Pattern.compile(
                        "(?i)(NoSuchBucket|NoSuchKey|404|Not.?Found|Access.?Denied|bucket)",
                    ),
            )
        }

        /** Replaces a field inside the `credential` JSON object. */
        private fun mutateCredentialField(
            baseConfig: String,
            field: String,
            value: String
        ): String {
            val config = mapper.readTree(baseConfig) as ObjectNode
            val credential = config.get("credential") as ObjectNode
            credential.put(field, value)
            return mapper.writeValueAsString(config)
        }

        /** Replaces a top-level field in the config JSON. */
        private fun mutateTopLevelField(baseConfig: String, field: String, value: String): String {
            val config = mapper.readTree(baseConfig) as ObjectNode
            config.put(field, value)
            return mapper.writeValueAsString(config)
        }
    }
}
