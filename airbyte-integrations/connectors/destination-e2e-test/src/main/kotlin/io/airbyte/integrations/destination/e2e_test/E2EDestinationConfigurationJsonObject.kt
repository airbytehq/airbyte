/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.e2e_test

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationJsonObjectBase
import jakarta.inject.Singleton

@JsonSchemaTitle("E2E Test Destination Spec")
@Singleton
class E2EDestinationConfigurationJsonObject : ConfigurationJsonObjectBase() {

    @JsonProperty("test_destination")
    @JsonSchemaTitle("Test Destination")
    @JsonPropertyDescription("The type of destination to be used.")
    val testDestination: TestDestination = LoggingDestination()

    @JsonProperty("record_batch_size_bytes")
    @JsonSchemaTitle("Record Batch Size Bytes")
    @JsonPropertyDescription("The maximum amount of record data to stage before processing.")
    val recordBatchSizeBytes: Long = 1024L * 1024L
}

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "test_destination_type"
)
@JsonSubTypes(
    JsonSubTypes.Type(value = LoggingDestination::class, name = "LOGGING"),
    JsonSubTypes.Type(value = SilentDestination::class, name = "SILENT"),
    JsonSubTypes.Type(value = ThrottledDestination::class, name = "THROTTLED"),
    JsonSubTypes.Type(value = FailingDestination::class, name = "FAILING")
)
sealed class TestDestination(
    @JsonProperty("test_destination_type") open val testDestinationType: Type
) {
    enum class Type(val typeName: String) {
        LOGGING("LOGGING"),
        SILENT("SILENT"),
        THROTTLED("THROTTLED"),
        FAILING("FAILING")
    }
}

data class LoggingDestination(
    @JsonProperty("test_destination_type") override val testDestinationType: Type = Type.LOGGING,
    @JsonProperty("logging_config") val loggingConfig: LoggingConfig = FirstNEntriesConfig()
) : TestDestination(testDestinationType)

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "logging_type"
)
@JsonSubTypes(
    JsonSubTypes.Type(value = FirstNEntriesConfig::class, name = "FirstN"),
    JsonSubTypes.Type(value = EveryNthEntryConfig::class, name = "EveryNth"),
    JsonSubTypes.Type(value = RandomSamplingConfig::class, name = "RandomSampling")
)
sealed class LoggingConfig(
    @JsonProperty("logging_type") open val loggingType: Type = Type.FIRST_N
) {
    enum class Type(@get:JsonValue val typeName: String) {
        FIRST_N("FirstN"),
        EVERY_NTH("EveryNth"),
        RANDOM_SAMPLING("RandomSampling")
    }
}

data class FirstNEntriesConfig(
    @JsonProperty("logging_type") override val loggingType: Type = Type.FIRST_N,
    @JsonProperty("max_entry_count") val maxEntryCount: Int = 100
) : LoggingConfig(loggingType)

data class EveryNthEntryConfig(
    @JsonProperty("logging_type") override val loggingType: Type = Type.EVERY_NTH,
    @JsonProperty("nth_entry_to_log") val nthEntryToLog: Int,
    @JsonProperty("max_entry_count") val maxEntryCount: Int = 100
) : LoggingConfig(loggingType)

data class RandomSamplingConfig(
    @JsonProperty("logging_type") override val loggingType: Type = Type.RANDOM_SAMPLING,
    @JsonProperty("sampling_ratio") val samplingRatio: Double = 0.001,
    @JsonProperty("seed") val seed: Long?,
    @JsonProperty("max_entry_count") val maxEntryCount: Int = 100
) : LoggingConfig(loggingType)

data class SilentDestination(
    @JsonProperty("test_destination_type") override val testDestinationType: Type = Type.SILENT
) : TestDestination(testDestinationType)

data class ThrottledDestination(
    @JsonProperty("test_destination_type") override val testDestinationType: Type = Type.THROTTLED,
    @JsonProperty("millis_per_record") val millisPerRecord: Long
) : TestDestination(testDestinationType)

data class FailingDestination(
    @JsonProperty("test_destination_type") override val testDestinationType: Type = Type.FAILING,
    @JsonProperty("num_messages") val numMessages: Int
) : TestDestination(testDestinationType)
