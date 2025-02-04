package io.airbyte.cdk.test.fixtures.legacy

import io.github.oshai.kotlinlogging.KotlinLogging
import java.util.function.Supplier

private val LOGGER = KotlinLogging.logger {}

/**
 * This class launches different variants of a source connector based on where Airbyte is deployed.
 */
object AdaptiveSourceRunner {

    const val DEPLOYMENT_MODE_KEY: String = EnvVariableFeatureFlags.Companion.DEPLOYMENT_MODE
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
                LOGGER.info { "Running source under deployment mode: $deploymentMode" }
                if (deploymentMode != null && deploymentMode == CLOUD_MODE) {
                    return cloudSourceSupplier.get()
                }
                if (deploymentMode == null) {
                    LOGGER.warn { "Deployment mode is null, default to OSS mode" }
                }
                return ossSourceSupplier.get()
            }

        @Throws(Exception::class)
        fun run(args: Array<String>) {
            val source = source
            LOGGER.info { "Starting source: ${source.javaClass.name}" }
            IntegrationRunner(source).run(args)
            LOGGER.info { "Completed source: ${source.javaClass.name}" }
        }
    }
}
