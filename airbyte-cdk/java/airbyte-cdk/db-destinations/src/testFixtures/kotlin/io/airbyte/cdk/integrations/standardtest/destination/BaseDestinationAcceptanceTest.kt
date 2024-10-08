package io.airbyte.cdk.integrations.standardtest.destination

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.commons.features.EnvVariableFeatureFlags
import io.airbyte.commons.features.FeatureFlags
import io.airbyte.commons.features.FeatureFlagsWrapper
import io.airbyte.protocol.models.v0.AirbyteMessage
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConnectorSpecification
import io.airbyte.protocol.models.v0.DestinationSyncMode
import io.airbyte.workers.exception.TestHarnessException
import io.airbyte.workers.process.ProcessFactory
import org.junit.jupiter.api.Assertions
import java.nio.file.Path
import java.util.HashSet

interface BaseDestinationAcceptanceTest {
    val imageName: String
        /**
         * Name of the docker image that the tests will run against.
         *
         * @return docker image name
         */
        get

    val verifyIndividualStateAndCounts: Boolean

    var testEnv: AbstractDestinationAcceptanceTest.TestDestinationEnv

    val imageNameWithoutTag: String
        get() =
            if (imageName.contains(":"))
                imageName.split(":".toRegex()).dropLastWhile { it.isEmpty() }.toTypedArray()[0]
            else imageName

    var processFactory: ProcessFactory
    var jobRoot: Path
    val isCloudTest: Boolean

    val featureFlags: FeatureFlags
        get() =
            if (isCloudTest) {
                FeatureFlagsWrapper.overridingDeploymentMode(EnvVariableFeatureFlags(), "CLOUD")
            } else {
                FeatureFlagsWrapper.overridingDeploymentMode(EnvVariableFeatureFlags(), "OSS")
            }

    /**
     * Configuration specific to the integration. Will be passed to integration where appropriate in
     * each test. Should be valid.
     *
     * @return integration-specific configuration
     */
    @Throws(Exception::class)
    fun getConfig(): JsonNode

    /**
     * Function that performs any setup of external resources required for the test. e.g.
     * instantiate a postgres database. This function will be called before EACH test.
     *
     * @param testEnv
     * - information about the test environment.
     * @param TEST_SCHEMAS
     * @throws Exception
     * - can throw any exception, test framework will handle.
     */
    @Throws(Exception::class)
    fun setup(testEnv: AbstractDestinationAcceptanceTest.TestDestinationEnv, TEST_SCHEMAS: HashSet<String>)


    fun runSpec(): ConnectorSpecification

    /**
     * Function that performs any clean up of external resources required for the test. e.g. delete
     * a postgres database. This function will be called after EACH test. It MUST remove all data in
     * the destination so that there is no contamination across tests.
     *
     * @param testEnv
     * - information about the test environment.
     * @throws Exception
     * - can throw any exception, test framework will handle.
     */
    @Throws(Exception::class) fun tearDown(testEnv: AbstractDestinationAcceptanceTest.TestDestinationEnv)

    fun runSyncAndVerifyStateOutput(
        config: JsonNode,
        messages: List<AirbyteMessage>,
        catalog: ConfiguredAirbyteCatalog,
        runNormalization: Boolean,
    ) {
        runSyncAndVerifyStateOutput(
            config,
            messages,
            catalog,
            runNormalization,
            imageName,
            verifyIndividualStateAndCounts
        )
    }

    fun runSyncAndVerifyStateOutput(
        config: JsonNode,
        messages: List<AirbyteMessage>,
        catalog: ConfiguredAirbyteCatalog,
        runNormalization: Boolean,
        imageName: String,
        verifyIndividualStateAndCounts: Boolean
    )

    /**
     * Detects if a destination implements overwrite mode from the spec.json that should include
     * 'supportedDestinationSyncMode'
     *
     * @return
     * - a boolean.
     */
    @Throws(TestHarnessException::class)
    fun implementsOverwrite(): Boolean {
        val spec = runSpec()
        Assertions.assertNotNull(spec)
        return if (spec.supportedDestinationSyncModes != null) {
            spec.supportedDestinationSyncModes.contains(DestinationSyncMode.OVERWRITE)
        } else {
            false
        }
    }

    /**
     * The method should be overridden if destination connector support newer protocol version
     * otherwise [io.airbyte.cdk.integrations.standardtest.destination.ProtocolVersion.V0] is used
     *
     * NOTE: Method should be public in a sake of java reflection
     *
     * @return
     */
    fun getProtocolVersion(): ProtocolVersion = ProtocolVersion.V0

    fun supportsInDestinationNormalization(): Boolean {
        return false
    }
}
