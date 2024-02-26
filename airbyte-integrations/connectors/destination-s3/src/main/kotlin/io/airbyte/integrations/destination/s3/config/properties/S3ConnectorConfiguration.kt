/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.s3.config.properties

import com.fasterxml.jackson.annotation.JsonIgnoreProperties
import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.core.config.ConnectorConfiguration
import io.micronaut.context.annotation.ConfigurationBuilder
import io.micronaut.context.annotation.ConfigurationProperties
import java.util.Optional

@ConfigurationProperties("airbyte.connector.config")
@JsonIgnoreProperties(value = ["loadingMethodBuilder", "rawNamespace"])
class S3ConnectorConfiguration : ConnectorConfiguration {
    @JsonProperty("access_key_id")
    var accessKeyId: String? = null

    @JsonProperty("file_name_pattern")
    var fileNamePattern: String? = null

    @JsonProperty("s3_bucket_name")
    var s3BucketName: String? = null

    @JsonProperty("s3_bucket_path")
    var s3BucketPath: String? = null

    @JsonProperty("s3_bucket_region")
    var s3BucketRegion: String? = null

    @JsonProperty("s3_endpoint")
    var s3Endpoint: String? = null

    @JsonProperty("s3_path_format")
    var s3PathFormat: String? = null

    @JsonProperty("secret_access_key")
    var secretAccessKey: String? = null

    @ConfigurationBuilder(prefixes = ["with"], configurationPrefix = "format")
    val format: S3ConnectorOutputFormat.Builder = S3ConnectorOutputFormat.Builder()

    override fun getRawNamespace(): Optional<String> {
        return Optional.empty<String>()
    }
}
