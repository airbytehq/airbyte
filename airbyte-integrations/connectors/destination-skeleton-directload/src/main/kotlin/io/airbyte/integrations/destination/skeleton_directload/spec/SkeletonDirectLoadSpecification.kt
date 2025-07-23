/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.skeleton_directload.spec

import com.fasterxml.jackson.annotation.JsonProperty
import com.fasterxml.jackson.annotation.JsonPropertyDescription
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaInject
import com.kjetland.jackson.jsonSchema.annotations.JsonSchemaTitle
import io.airbyte.cdk.command.ConfigurationSpecification
import jakarta.inject.Singleton

@Singleton
class SkeletonDirectLoadSpecification : ConfigurationSpecification() {
    @get:JsonSchemaTitle("Namespace")
    @get:JsonPropertyDescription(
        """The namespace""",
    )
    @get:JsonProperty("namespace")
    @get:JsonSchemaInject(json = """{"order": 0}""")
    val namespace: String = ""
}
