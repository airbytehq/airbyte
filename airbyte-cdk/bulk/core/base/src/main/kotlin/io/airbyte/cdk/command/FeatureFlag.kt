/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.command

import io.micronaut.context.annotation.Factory
import io.micronaut.context.annotation.Value
import io.micronaut.context.env.Environment
import jakarta.inject.Singleton
import java.util.EnumSet

/**
 * An enum of all feature flags, currently these are set via environment vars.
 *
 * Micronaut can inject a Set<FeatureFlag> singleton of all active feature flags.
 */
enum class FeatureFlag(
    val micronautEnvironmentName: String,
    val envVar: EnvVar,
    val requiredEnvVarValue: String,
    private val transformActualValue: (String) -> String = { it }
) {

    /** [AIRBYTE_CLOUD_DEPLOYMENT] is active when the connector is running in Airbyte Cloud. */
    AIRBYTE_CLOUD_DEPLOYMENT(
        micronautEnvironmentName = AIRBYTE_CLOUD_ENV,
        envVar = EnvVar.DEPLOYMENT_MODE,
        requiredEnvVarValue = "CLOUD",
        transformActualValue = { it.trim().uppercase() },
    );

    /** Environment variable binding shell declaration which activates the feature flag. */
    val envVarBindingDeclaration: String
        get() = "${envVar.name}=$requiredEnvVarValue"

    enum class EnvVar(val defaultValue: String = "") {
        DEPLOYMENT_MODE
    }

    companion object {
        internal fun active(systemEnv: Map<String, String>): List<FeatureFlag> =
            entries.filter { featureFlag: FeatureFlag ->
                val envVar: EnvVar = featureFlag.envVar
                val envVarValue: String = systemEnv[envVar.name] ?: envVar.defaultValue
                featureFlag.transformActualValue(envVarValue) == featureFlag.requiredEnvVarValue
            }
    }

    @Factory
    private class MicronautFactory {

        @Singleton
        fun active(environment: Environment): Set<FeatureFlag> =
            EnumSet.noneOf(FeatureFlag::class.java).apply {
                addAll(
                    FeatureFlag.entries.filter {
                        environment.activeNames.contains(it.micronautEnvironmentName)
                    }
                )
            }
    }
}

const val AIRBYTE_CLOUD_ENV = "airbyte-cloud"

const val AIRBYTE_DEPLOYMENT_MODE_PROPERTY = "airbyte.core.deployment.mode"
const val DEPLOYMENT_MODE_CLOUD = "CLOUD"

enum class DeploymentMode { OSS, CLOUD }
@Factory
class DeploymentModeFactory(@Value("\${airbyte.core.deployment.mode}") val deploymentMode: String?) {
    @Singleton
    fun getDeploymentMode(): DeploymentMode {
        return when (deploymentMode) {
            "CLOUD" -> DeploymentMode.CLOUD
            "OSS" -> DeploymentMode.OSS
            // if deployment mode is unset, or some weird value, assume OSS
            else -> DeploymentMode.OSS
        }
    }
}
