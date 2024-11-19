/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.command.aws

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle

interface AWSArnRoleSpecification {
    @get:JsonSchemaTitle("Role ARN")
    @get:JsonPropertyDescription("The Role ARN.")
    @get:JsonProperty("role_arn")
    @get:JsonSchemaInject(
        json = """{"examples":["arn:aws:iam::123456789:role/ExternalIdIsYourWorkspaceId"]}"""
    )
    val roleArn: String?

    fun toAWSArnRoleConfiguration(): AWSArnRoleConfiguration {
        return AWSArnRoleConfiguration(roleArn)
    }
}

data class AWSArnRoleConfiguration(val roleArn: String?)

interface AWSArnRoleConfigurationProvider {
    val awsArnRoleConfiguration: AWSArnRoleConfiguration
}
