/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3_data_lake.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.load.command.DestinationConfiguration
import io.airbyte.cdk.load.command.DestinationConfigurationFactory
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfiguration
import io.airbyte.cdk.load.command.aws.AWSAccessKeyConfigurationProvider
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfiguration
import io.airbyte.cdk.load.command.iceberg.parquet.IcebergCatalogConfigurationProvider
import io.micronaut.context.annotation.Factory
import jakarta.inject.Singleton

const val DEFAULT_CATALOG_NAME = "airbyte"
const val DEFAULT_STAGING_BRANCH = "airbyte_staging"
const val TEST_TABLE = "airbyte_test_table"

data class S3DataLakeConfiguration(
    override val awsAccessKeyConfiguration: AWSAccessKeyConfiguration,
    override val s3BucketConfiguration: S3BucketConfiguration,
    override val icebergCatalogConfiguration: IcebergCatalogConfiguration,
    val flushBatchSizeMb: Long?,
    val primaryKeyBloomFilter: PrimaryKeyBloomFilterConfiguration =
        PrimaryKeyBloomFilterConfiguration(),
) :
    DestinationConfiguration(),
    AWSAccessKeyConfigurationProvider,
    IcebergCatalogConfigurationProvider,
    S3BucketConfigurationProvider {

    object Defaults {
        const val MIN_FLUSH_BATCH_SIZE_MB = 1L
        const val FLUSH_BATCH_SIZE_MB = 200L
        const val MAX_FLUSH_BATCH_SIZE_MB = 500L
    }

    val resolvedFlushBatchSizeBytes: Long
        get() {
            val mb = flushBatchSizeMb ?: Defaults.FLUSH_BATCH_SIZE_MB
            require(mb >= Defaults.MIN_FLUSH_BATCH_SIZE_MB) {
                "flush_batch_size_mb must be at least ${Defaults.MIN_FLUSH_BATCH_SIZE_MB}, got $mb"
            }
            require(mb <= Defaults.MAX_FLUSH_BATCH_SIZE_MB) {
                "flush_batch_size_mb must be at most ${Defaults.MAX_FLUSH_BATCH_SIZE_MB}, got $mb"
            }
            return mb * 1024L * 1024L
        }
}

data class PrimaryKeyBloomFilterConfiguration(
    @get:JsonSchemaTitle("Enabled")
    @get:JsonPropertyDescription(
        "Whether to enable the experimental primary-key Bloom filter optimization."
    )
    @get:JsonSchemaInject(json = """{"default": false, "order": 0}""")
    val enabled: Boolean = false,

    @get:JsonSchemaTitle("Expected Items")
    @get:JsonPropertyDescription(
        "Expected number of unique primary keys to add to the Bloom filter during one sync."
    )
    @param:JsonProperty("expected_items")
    @get:JsonProperty("expected_items")
    @get:JsonSchemaInject(json = """{"default": 10000000, "order": 1}""")
    val expectedItems: Int = Defaults.EXPECTED_ITEMS,

    @get:JsonSchemaTitle("Number of Bits")
    @get:JsonPropertyDescription("Number of bits in the Bloom filter.")
    @param:JsonProperty("num_bits")
    @get:JsonProperty("num_bits")
    @get:JsonSchemaInject(json = """{"default": 100000000, "order": 2}""")
    val numberOfBits: Int = Defaults.NUMBER_OF_BITS,

    @get:JsonSchemaTitle("Number of Hash Functions")
    @get:JsonPropertyDescription("Number of hash functions to use for each primary key.")
    @param:JsonProperty("num_hash_functions")
    @get:JsonProperty("num_hash_functions")
    @get:JsonSchemaInject(json = """{"default": 7, "order": 3}""")
    val numberOfHashFunctions: Int = Defaults.NUMBER_OF_HASH_FUNCTIONS,

    @get:JsonSchemaTitle("Log Interval Records")
    @get:JsonPropertyDescription(
        "How often to log Bloom filter counters by number of checked keys. Set to 0 to disable periodic logging."
    )
    @param:JsonProperty("log_interval_records")
    @get:JsonProperty("log_interval_records")
    @get:JsonSchemaInject(json = """{"default": 1000000, "order": 4}""")
    val logIntervalRecords: Long = Defaults.LOG_INTERVAL_RECORDS,
) {
    object Defaults {
        const val EXPECTED_ITEMS = 10_000_000
        const val NUMBER_OF_BITS = 100_000_000
        const val NUMBER_OF_HASH_FUNCTIONS = 7
        const val LOG_INTERVAL_RECORDS = 1_000_000L
    }

    init {
        require(expectedItems > 0) { "primary_key_bloom_filter.expected_items must be positive" }
        require(numberOfBits > 0) { "primary_key_bloom_filter.num_bits must be positive" }
        require(numberOfHashFunctions > 0) {
            "primary_key_bloom_filter.num_hash_functions must be positive"
        }
        require(logIntervalRecords >= 0) {
            "primary_key_bloom_filter.log_interval_records must be non-negative"
        }
    }
}

@Singleton
class S3DataLakeConfigurationFactory :
    DestinationConfigurationFactory<S3DataLakeSpecification, S3DataLakeConfiguration> {

    override fun makeWithoutExceptionHandling(
        pojo: S3DataLakeSpecification
    ): S3DataLakeConfiguration {
        return S3DataLakeConfiguration(
            awsAccessKeyConfiguration = pojo.toAWSAccessKeyConfiguration(),
            s3BucketConfiguration = pojo.toS3BucketConfiguration(),
            icebergCatalogConfiguration = pojo.toIcebergCatalogConfiguration(),
            flushBatchSizeMb = pojo.flushBatchSizeMb,
            primaryKeyBloomFilter =
                pojo.primaryKeyBloomFilter ?: PrimaryKeyBloomFilterConfiguration(),
        )
    }
}

@Factory
class S3DataLakeConfigurationProvider(private val config: DestinationConfiguration) {
    @Singleton
    fun get(): S3DataLakeConfiguration {
        return config as S3DataLakeConfiguration
    }
}
