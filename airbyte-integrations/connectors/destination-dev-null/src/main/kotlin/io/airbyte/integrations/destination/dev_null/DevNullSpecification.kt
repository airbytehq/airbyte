/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.dev_null

import com.fasterxml.jackson.annotation.JsonClassDescription
import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.fasterxml.jackson.annotation.JsonSubTypes
import com.fasterxml.jackson.annotation.JsonTypeInfo
import com.fasterxml.jackson.annotation.JsonValue
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.AIRBYTE_CLOUD_ENV
import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.spec.DestinationSpecificationExtension
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.context.annotation.Requires
import jakarta.inject.Singleton
import javax.validation.constraints.Max
import javax.validation.constraints.Min

sealed class TestDestination

sealed class DevNullSpecification : ConfigurationSpecification() {
    abstract val testDestination: TestDestination
}

/**
 * This doesn't quite conform with the old spec:
 * - Some fields that make more sense as integral need to be Double to yield a "number" type
 * - Due to https://github.com/mbknor/mbknor-jackson-jsonSchema/issues/184, this causes
 * ```
 *    `@JsonSchemaExamples` to break. Instead, we inject a raw JSON blob to the schema.
 * ```
 * - Similarly, there are some cases where [JsonSchemaTitle] / [JsonClassDescription]
 * ```
 *    don't work as expected. In these cases, we also inject raw JSON.
 * ```
 * - Additionally, there are extra fields:
 * ```
 *    - "additionalProperties: true" appears throughout (not helped by @JsonIgnoreProperties)
 *    - "type": "object" is appended to the case classes
 * ```
 */
@JsonSchemaTitle("E2E Test Destination Spec")
@Singleton
@Requires(notEnv = [AIRBYTE_CLOUD_ENV])
class DevNullSpecificationOss : DevNullSpecification() {
    @JsonProperty("test_destination")
    @JsonSchemaTitle("Test Destination")
    @JsonPropertyDescription("The type of destination to be used")
    override val testDestination: TestDestinationOSS = LoggingDestination()
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
sealed class TestDestinationOSS(
    @JsonProperty("test_destination_type") open val testDestinationType: Type
) : TestDestination() {
    enum class Type(val typeName: String) {
        LOGGING("LOGGING"),
        SILENT("SILENT"),
        THROTTLED("THROTTLED"),
        FAILING("FAILING")
    }
}

@JsonSchemaTitle("Logging")
data class LoggingDestination(
    @JsonProperty("test_destination_type") override val testDestinationType: Type = Type.LOGGING,
    @JsonPropertyDescription("Configurate how the messages are logged.")
    @JsonProperty("logging_config")
    val loggingConfig: LoggingConfig = FirstNEntriesConfig()
) : TestDestinationOSS(testDestinationType)

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
@JsonSchemaInject(json = """{"title":"Logging Configuration"}""")
sealed class LoggingConfig(
    @JsonProperty("logging_type") open val loggingType: Type = Type.FIRST_N
) {
    enum class Type(@get:JsonValue val typeName: String) {
        FIRST_N("FirstN"),
        EVERY_NTH("EveryNth"),
        RANDOM_SAMPLING("RandomSampling")
    }
}

@JsonSchemaTitle("First N Entries")
@JsonSchemaInject(json = """{"description":"Log first N entries per stream."}""")
data class FirstNEntriesConfig(
    @JsonProperty("logging_type") override val loggingType: Type = Type.FIRST_N,
    @JsonSchemaTitle("N")
    @JsonPropertyDescription(
        "Number of entries to log. This destination is for testing only. So it won't make sense to log infinitely. The maximum is 1,000 entries."
    )
    @JsonProperty("max_entry_count", defaultValue = "100")
    @JsonSchemaInject(json = """{"examples":[100]}""")
    @Max(1000)
    @Min(1)
    val maxEntryCount: Double = 100.0
) : LoggingConfig(loggingType)

@JsonSchemaTitle("Every N-th Entry")
@JsonSchemaInject(
    json = """{"description":"For each stream, log every N-th entry with a maximum cap."}"""
)
data class EveryNthEntryConfig(
    @JsonProperty("logging_type") override val loggingType: Type = Type.EVERY_NTH,
    @JsonSchemaTitle("N")
    @JsonPropertyDescription(
        "The N-th entry to log for each stream. N starts from 1. For example, when N = 1, every entry is logged; when N = 2, every other entry is logged; when N = 3, one out of three entries is logged."
    )
    @JsonProperty("nth_entry_to_log")
    @JsonSchemaInject(json = """{"examples":[3]}""")
    @Max(1000)
    @Min(1)
    val nthEntryToLog: Int,
    @JsonSchemaTitle("Max Log Entries")
    @JsonPropertyDescription(
        "Number of entries to log. This destination is for testing only. So it won't make sense to log infinitely. The maximum is 1,000 entries."
    )
    @JsonProperty("max_entry_count", defaultValue = "100")
    @JsonSchemaInject(json = """{"examples":[100]}""")
    @Max(1000)
    @Min(1)
    val maxEntryCount: Double
) : LoggingConfig(loggingType)

@JsonSchemaTitle("Random Sampling")
@JsonSchemaInject(
    json =
        """{"description":"For each stream, randomly log a percentage of the entries with a maximum cap."}"""
)
data class RandomSamplingConfig(
    @JsonProperty("logging_type") override val loggingType: Type = Type.RANDOM_SAMPLING,
    @JsonSchemaTitle("Sampling Ratio")
    @JsonPropertyDescription("A positive floating number smaller than 1.")
    @JsonProperty("sampling_ratio")
    @JsonSchemaInject(json = """{"examples":[0.001],"default":0.001}""")
    @Max(1)
    @Min(0)
    val samplingRatio: Double = 0.001,
    @JsonSchemaTitle("Random Number Generator Seed")
    @JsonPropertyDescription(
        "When the seed is unspecified, the current time millis will be used as the seed."
    )
    @JsonSchemaInject(json = """{"examples":[1900]}""")
    @JsonProperty("seed")
    val seed: Double? = null,
    @JsonSchemaTitle("Max Log Entries")
    @JsonPropertyDescription(
        "Number of entries to log. This destination is for testing only. So it won't make sense to log infinitely. The maximum is 1,000 entries."
    )
    @JsonProperty("max_entry_count", defaultValue = "100")
    @JsonSchemaInject(json = """{"examples":[100]}""")
    @Max(1000)
    @Min(1)
    val maxEntryCount: Double = 100.0
) : LoggingConfig(loggingType)

@JsonSchemaTitle("Silent")
data class SilentDestination(
    @JsonProperty("test_destination_type") override val testDestinationType: Type = Type.SILENT
) : TestDestinationOSS(testDestinationType)

@JsonSchemaTitle("Throttled")
data class ThrottledDestination(
    @JsonProperty("test_destination_type") override val testDestinationType: Type = Type.THROTTLED,
    @JsonPropertyDescription("The number of milliseconds to wait between each record.")
    @JsonProperty("millis_per_record")
    val millisPerRecord: Long
) : TestDestinationOSS(testDestinationType)

@JsonSchemaTitle("Failing")
data class FailingDestination(
    @JsonProperty("test_destination_type") override val testDestinationType: Type = Type.FAILING,
    @JsonPropertyDescription("Number of messages after which to fail.")
    @JsonProperty("num_messages")
    val numMessages: Int
) : TestDestinationOSS(testDestinationType)

/** The cloud variant is more restricted: it only allows for a single destination type. */
@JsonSchemaTitle("E2E Test Destination Spec")
@Singleton
@Requires(env = [AIRBYTE_CLOUD_ENV])
class DevNullSpecificationCloud : DevNullSpecification() {
    @JsonProperty("test_destination")
    @JsonSchemaTitle("Test Destination")
    @JsonPropertyDescription("The type of destination to be used")
    override val testDestination: TestDestinationCloud = SilentDestinationCloud()
}

@JsonTypeInfo(
    use = JsonTypeInfo.Id.NAME,
    include = JsonTypeInfo.As.EXISTING_PROPERTY,
    property = "test_destination_type"
)
@JsonSubTypes(
    JsonSubTypes.Type(value = SilentDestinationCloud::class, name = "SILENT"),
)
sealed class TestDestinationCloud(
    @JsonProperty("test_destination_type") open val testDestinationType: Type
) : TestDestination() {
    enum class Type(val typeName: String) {
        SILENT("SILENT"),
    }
}

@JsonSchemaTitle("Silent")
data class SilentDestinationCloud(
    @JsonProperty("test_destination_type") override val testDestinationType: Type = Type.SILENT
) : TestDestinationCloud(testDestinationType)

/** Non-client-facing configuration. */
@Singleton
class DevNullSpecificationExtension : DestinationSpecificationExtension {
    override val supportedSyncModes =
        listOf(
            DestinationSyncMode.OVERWRITE,
            DestinationSyncMode.APPEND,
            DestinationSyncMode.APPEND_DEDUP,
        )
    override val supportsIncremental = true
}
