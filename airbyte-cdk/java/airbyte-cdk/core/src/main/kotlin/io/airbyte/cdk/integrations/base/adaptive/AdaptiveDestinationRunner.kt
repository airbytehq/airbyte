/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.base.adaptive

import io.airbyte.cdk.integrations.base.Destination
import io.airbyte.cdk.integrations.base.IntegrationRunner
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.function.Supplier

private val LOGGER = KotlinLogging.logger {}
/**
 * This class launches different variants of a destination connector based on where Airbyte is
 * deployed.
 */
object AdaptiveDestinationRunner {

    private const val DEPLOYMENT_MODE_KEY = EnvVariableFeatureFlags.DEPLOYMENT_MODE
    private const val CLOUD_MODE = "CLOUD"

    @JvmStatic
    fun baseOnEnv(): OssDestinationBuilder {
        val mode = System.getenv(DEPLOYMENT_MODE_KEY)
        return OssDestinationBuilder(mode)
    }

    class OssDestinationBuilder(private val deploymentMode: String?) {
        fun <OT : Destination> withOssDestination(
            ossDestinationSupplier: Supplier<OT>
        ): CloudDestinationBuilder<OT> {
            return CloudDestinationBuilder(deploymentMode, ossDestinationSupplier)
        }
    }

    class CloudDestinationBuilder<OT : Destination>(
        private val deploymentMode: String?,
        private val ossDestinationSupplier: Supplier<OT>
    ) {
        fun <CT : Destination> withCloudDestination(
            cloudDestinationSupplier: Supplier<CT>
        ): Runner<OT, CT> {
            return Runner(deploymentMode, ossDestinationSupplier, cloudDestinationSupplier)
        }
    }

    class Runner<OT : Destination, CT : Destination>(
        private val deploymentMode: String?,
        private val ossDestinationSupplier: Supplier<OT>,
        private val cloudDestinationSupplier: Supplier<CT>
    ) {
        private val destination: Destination
            get() {
                LOGGER.info { "Running destination under deployment mode: $deploymentMode" }
                if (deploymentMode != null && deploymentMode == CLOUD_MODE) {
                    return cloudDestinationSupplier.get()
                }
                if (deploymentMode == null) {
                    LOGGER.warn { "Deployment mode is null, default to OSS mode" }
                }
                return ossDestinationSupplier.get()
            }

        @Throws(Exception::class)
        fun run(args: Array<String>) {
            val destination = destination
            LOGGER.info { "Starting destination: ${destination.javaClass.name}" }
            IntegrationRunner(destination).run(args)
            LOGGER.info { "Completed destination: ${destination.javaClass.name}" }
        }
    }
}
