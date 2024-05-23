/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.source

import io.airbyte.commons.lang.Exceptions
import io.airbyte.commons.map.MoreMaps
import io.airbyte.commons.version.AirbyteVersion
import java.util.*
import java.util.function.Function
import java.util.function.Supplier
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * This class passes environment variable to the DockerProcessFactory that runs the source in the
 * SourceAcceptanceTest.
 */
// todo (cgardens) - this cloud_deployment implicit interface is going to bite us.
class TestEnvConfigs private constructor(envMap: Map<String, String>) {
    enum class DeploymentMode {
        OSS,
        CLOUD
    }

    enum class WorkerEnvironment {
        DOCKER,
        KUBERNETES
    }

    private val getEnv = Function { key: String -> envMap.getValue(key) }
    private val getAllEnvKeys = Supplier { envMap.keys }

    constructor() : this(System.getenv())

    val airbyteRole: String
        // CORE
        get() = getEnv(AIRBYTE_ROLE)

    val airbyteVersion: AirbyteVersion
        get() = AirbyteVersion(getEnsureEnv(AIRBYTE_VERSION))

    val deploymentMode: DeploymentMode
        get() =
            getEnvOrDefault(DEPLOYMENT_MODE, DeploymentMode.OSS) { s: String ->
                try {
                    return@getEnvOrDefault DeploymentMode.valueOf(s)
                } catch (e: IllegalArgumentException) {
                    LOGGER.info(s + " not recognized, defaulting to " + DeploymentMode.OSS)
                    return@getEnvOrDefault DeploymentMode.OSS
                }
            }

    val workerEnvironment: WorkerEnvironment
        get() =
            getEnvOrDefault(WORKER_ENVIRONMENT, WorkerEnvironment.DOCKER) { s: String ->
                WorkerEnvironment.valueOf(s.uppercase(Locale.getDefault()))
            }

    val jobDefaultEnvMap: Map<String, String>
        /**
         * There are two types of environment variables available to the job container:
         *
         * * Exclusive variables prefixed with JOB_DEFAULT_ENV_PREFIX
         * * Shared variables defined in JOB_SHARED_ENVS
         */
        get() {
            val jobPrefixedEnvMap =
                getAllEnvKeys
                    .get()
                    .filter { it.startsWith(JOB_DEFAULT_ENV_PREFIX) }
                    .associate { it.replace(JOB_DEFAULT_ENV_PREFIX, "") to getEnv(it) }

            // This method assumes that these shared env variables are not critical to the execution
            // of the jobs, and only serve as metadata. So any exception is swallowed and default to
            // an empty string. Change this logic if this assumption no longer holds.
            val jobSharedEnvMap =
                JOB_SHARED_ENVS.entries.associate {
                    it.key to Exceptions.swallowWithDefault({ it.value.apply(this) ?: "" }, "")
                }
            return MoreMaps.merge(jobPrefixedEnvMap, jobSharedEnvMap)
        }

    fun <T> getEnvOrDefault(key: String, defaultValue: T, parser: Function<String, T>): T {
        return getEnvOrDefault(key, defaultValue, parser, false)
    }

    fun <T> getEnvOrDefault(
        key: String,
        defaultValue: T,
        parser: Function<String, T>,
        isSecret: Boolean
    ): T {
        val value = getEnv.apply(key)
        if (value != null && !value.isEmpty()) {
            return parser.apply(value)
        } else {
            LOGGER.info(
                "Using default value for environment variable {}: '{}'",
                key,
                if (isSecret) "*****" else defaultValue
            )
            return defaultValue
        }
    }

    fun getEnv(name: String): String {
        return getEnv.apply(name)
    }

    fun getEnsureEnv(name: String): String {
        val value = getEnv(name)
        checkNotNull(value != null) { "$name environment variable cannot be null" }

        return value
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(TestEnvConfigs::class.java)

        // env variable names
        const val AIRBYTE_ROLE: String = "AIRBYTE_ROLE"
        const val AIRBYTE_VERSION: String = "AIRBYTE_VERSION"
        const val WORKER_ENVIRONMENT: String = "WORKER_ENVIRONMENT"
        const val DEPLOYMENT_MODE: String = "DEPLOYMENT_MODE"
        const val JOB_DEFAULT_ENV_PREFIX: String = "JOB_DEFAULT_ENV_"

        val JOB_SHARED_ENVS: Map<String, Function<TestEnvConfigs, String>> =
            java.util.Map.of(
                AIRBYTE_VERSION,
                Function { instance: TestEnvConfigs -> instance.airbyteVersion.serialize() },
                AIRBYTE_ROLE,
                Function { obj: TestEnvConfigs -> obj.airbyteRole },
                DEPLOYMENT_MODE,
                Function { instance: TestEnvConfigs -> instance.deploymentMode.name },
                WORKER_ENVIRONMENT,
                Function { instance: TestEnvConfigs -> instance.workerEnvironment.name }
            )
    }
}
