/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.aws

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

/**
 * Mix-in to a configuration to add AWS access key id and secret access key fields as properties.
 *
 * See [io.airbyte.cdk.load.command.DestinationConfiguration] for more details on how to use this
 * interface.
 */
interface AWSAccessKeySpecification {
    @get:JsonSchemaTitle("S3 Key ID")
    @get:JsonPropertyDescription(
        "The access key ID to access the S3 bucket. Airbyte requires Read and Write permissions to the given bucket. Read more <a href=\"https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys\">here</a>."
    )
    @get:JsonProperty("access_key_id")
    @get:JsonSchemaInject(json = """{"examples":["A012345678910EXAMPLE"]}""")
    val accessKeyId: String

    @get:JsonSchemaTitle("S3 Access Key")
    @get:JsonPropertyDescription(
        "The corresponding secret to the access key ID. Read more <a href=\"https://docs.aws.amazon.com/general/latest/gr/aws-sec-cred-types.html#access-keys-and-secret-access-keys\">here</a>"
    )
    @get:JsonProperty("secret_access_key")
    @get:JsonSchemaInject(json = """{"examples":["a012345678910ABCDEFGH/AbCdEfGhEXAMPLEKEY"]}""")
    val secretAccessKey: String

    fun toAWSAccessKeyConfiguration(): AWSAccessKeyConfiguration {
        return AWSAccessKeyConfiguration(accessKeyId, secretAccessKey)
    }
}

data class AWSAccessKeyConfiguration(val accessKeyId: String, val secretAccessKey: String)

interface AWSAccessKeyConfigurationProvider {
    val awsAccessKeyConfiguration: AWSAccessKeyConfiguration
}
