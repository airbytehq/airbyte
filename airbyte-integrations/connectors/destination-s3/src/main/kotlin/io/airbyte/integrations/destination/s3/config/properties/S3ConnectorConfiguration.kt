/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.config.properties

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.core.config.ConnectorConfiguration
import io.airbyte.cdk.core.config.annotation.AirbyteDisplayHint
import io.airbyte.cdk.core.config.annotation.ConnectorSpecificationDefinition
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.micronaut.context.annotation.ConfigurationBuilder
import io.micronaut.context.annotation.ConfigurationProperties
import java.util.Optional

@ConfigurationProperties("airbyte.connector.config")
@JsonIgnoreProperties(value = ["loadingMethodBuilder", "rawNamespace"])
@ConnectorSpecificationDefinition(
    changelogUrl =  "",
    documentationUrl = "https://docs.airbyte.com/integrations/destinations/s3",
    protocolVersion = "0.5.0",
    supportsIncremental = true,
    supportsNormalization = false,
    supportsDBT = false,
    supportedDestinationSyncModes = [DestinationSyncMode.OVERWRITE, DestinationSyncMode.APPEND]
)
class S3ConnectorConfiguration : ConnectorConfiguration {
    @JsonProperty("access_key_id")
    @AirbyteDisplayHint(
        alwaysShow = true,
        description = "The access key ID to access the S3 bucket. Airbyte requires Read and Write permissions to the given bucket. Read more <a href=\"https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys\">here</a>.",
        examples = ["A012345678910EXAMPLE"],
        order = 0,
        secret = true,
        title = "S3 Key ID")
    var accessKeyId: String? = null

    @JsonProperty("file_name_pattern")
    var fileNamePattern: String? = null

    @JsonProperty("s3_bucket_name", required = true)
    var s3BucketName: String? = null

    @JsonProperty("s3_bucket_path", required = true)
    var s3BucketPath: String? = null

    @JsonProperty("s3_bucket_region", required = true, defaultValue = "")
    var s3BucketRegion: String? = null

    @JsonProperty("s3_endpoint")
    var s3Endpoint: String? = null

    @JsonProperty("s3_path_format")
    var s3PathFormat: String? = null

    @JsonProperty("secret_access_key")
    var secretAccessKey: String? = null

    @ConfigurationBuilder(prefixes = ["with"], configurationPrefix = "format")
    val format: S3ConnectorOutputFormat.Builder = S3ConnectorOutputFormat.Builder()

    @JsonProperty("format", required = true)
    fun getOutputFormat(): S3ConnectorOutputFormat {
        return format.build()
    }
    override fun getDefaultNamespace(): Optional<String> {
        return Optional.empty<String>()
    }

    override fun getRawNamespace(): Optional<String> {
        return Optional.empty<String>()
    }
}
