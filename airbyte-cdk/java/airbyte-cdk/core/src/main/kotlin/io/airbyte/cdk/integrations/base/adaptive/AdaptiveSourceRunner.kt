/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base.adaptive

import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.cdk.integrations.base.Source
import io.airbyte.commons.features.EnvVariableFeatureFlags
import java.util.function.Supplier
import org.slf4j.Logger
import org.slf4j.LoggerFactory

/**
 * This class launches different variants of a source connector based on where Airbyte is deployed.
 */
object AdaptiveSourceRunner {
    private val LOGGER: Logger = LoggerFactory.getLogger(AdaptiveSourceRunner::class.java)

    const val DEPLOYMENT_MODE_KEY: String = EnvVariableFeatureFlags.DEPLOYMENT_MODE
    const val CLOUD_MODE: String = "CLOUD"

    fun baseOnEnv(): OssSourceBuilder {
        val mode = System.getenv(DEPLOYMENT_MODE_KEY)
        return OssSourceBuilder(mode)
    }

    class OssSourceBuilder(private val deploymentMode: String) {
        fun <OT : Source> withOssSource(ossSourceSupplier: Supplier<OT>): CloudSourceBuilder<OT> {
            return CloudSourceBuilder(deploymentMode, ossSourceSupplier)
        }
    }

    class CloudSourceBuilder<OT : Source>(
        private val deploymentMode: String,
        private val ossSourceSupplier: Supplier<OT>
    ) {
        fun <CT : Source> withCloudSource(cloudSourceSupplier: Supplier<CT>): Runner<OT, CT> {
            return Runner(deploymentMode, ossSourceSupplier, cloudSourceSupplier)
        }
    }

    class Runner<OT : Source, CT : Source>(
        private val deploymentMode: String?,
        private val ossSourceSupplier: Supplier<OT>,
        private val cloudSourceSupplier: Supplier<CT>
    ) {
        private val source: Source
            get() {
                LOGGER.info("Running source under deployment mode: {}", deploymentMode)
                if (deploymentMode != null && deploymentMode == CLOUD_MODE) {
                    return cloudSourceSupplier.get()
                }
                if (deploymentMode == null) {
                    LOGGER.warn("Deployment mode is null, default to OSS mode")
                }
                return ossSourceSupplier.get()
            }

        @Throws(Exception::class)
        fun run(args: Array<String>) {
            val source = source
            LOGGER.info("Starting source: {}", source.javaClass.name)
            IntegrationRunner(source).run(args)
            LOGGER.info("Completed source: {}", source.javaClass.name)
        }
    }
}
