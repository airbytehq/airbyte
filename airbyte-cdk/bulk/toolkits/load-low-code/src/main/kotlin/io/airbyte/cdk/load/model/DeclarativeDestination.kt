package io.airbyte.cdk.load.model

import com.fasterxml.jackson.annotation.JsonProperty
import io.airbyte.cdk.load.model.checker.Checker

/**
 * Root configuration for a declarative destination that uploads data according to its declarative components.
 */
data class DeclarativeDestination(
    @JsonProperty("checker")
    val checker: Checker
)

