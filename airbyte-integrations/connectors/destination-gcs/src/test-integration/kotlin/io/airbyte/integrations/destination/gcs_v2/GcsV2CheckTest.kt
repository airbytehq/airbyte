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
 * Check integration tests: verifies success with all formats and failure with bad credentials /
 * bucket. Configs are built from `secrets/config.json` with format injected in-memory.
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

        /** Builds failure configs by mutating a valid config with bad credentials or bucket. */
        private fun buildFailConfigs(): Map<CheckTestConfig, Pattern> {
            val baseConfig = GcsV2TestUtils.getConfigWithFormat(GcsV2TestUtils.JSONL_FORMAT)
            return mapOf(
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

        private fun mutateTopLevelField(baseConfig: String, field: String, value: String): String {
            val config = mapper.readTree(baseConfig) as ObjectNode
            config.put(field, value)
            return mapper.writeValueAsString(config)
        }
    }
}
