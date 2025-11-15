/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.aws

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

interface AWSArnRoleSpecification {
    @get:JsonSchemaTitle("Role ARN")
    @get:JsonPropertyDescription("The ARN of the AWS role to assume. Only usable in Airbyte Cloud.")
    @get:JsonProperty("role_arn")
    val roleArn: String?

    fun toAWSArnRoleConfiguration(): AWSArnRoleConfiguration {
        return AWSArnRoleConfiguration(roleArn)
    }
}

data class AWSArnRoleConfiguration(val roleArn: String?)

interface AWSArnRoleConfigurationProvider {
    val awsArnRoleConfiguration: AWSArnRoleConfiguration
}
