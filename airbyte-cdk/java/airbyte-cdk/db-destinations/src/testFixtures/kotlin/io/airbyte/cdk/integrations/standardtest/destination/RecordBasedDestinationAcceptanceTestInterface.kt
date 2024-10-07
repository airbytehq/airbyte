package io.airbyte.cdk.integrations.standardtest.destination

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.integrations.destination.NamingConventionTransformer
import io.airbyte.cdk.integrations.standardtest.destination.argproviders.DataTypeTestArgumentProvider
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.resources.MoreResources
import io.airbyte.commons.util.MoreIterators
import io.airbyte.configoss.StandardCheckConnectionOutput
import io.airbyte.protocol.models.v0.*
import io.airbyte.workers.process.ProcessFactory
import org.junit.jupiter.api.extension.ExtensionContext
import org.junit.jupiter.params.provider.Arguments
import org.junit.jupiter.params.provider.ArgumentsProvider
import java.io.IOException
import java.nio.file.Path
import java.util.*
import java.util.function.Consumer
import java.util.stream.Stream

interface RecordBasedDestinationAcceptanceTestInterface {
    fun runSpec(): ConnectorSpecification
    fun runCheck(config: JsonNode?): StandardCheckConnectionOutput
    fun getConfig(): JsonNode
    fun getFailCheckConfig(): JsonNode?
    fun getDefaultSchema(config: JsonNode): String?
    fun runSyncAndVerifyStateOutput(
        config: JsonNode,
        messages: List<AirbyteMessage>,
        catalog: ConfiguredAirbyteCatalog,
        runNormalization: Boolean,
    )
    fun retrieveRawRecordsAndAssertSameMessages(
        catalog: AirbyteCatalog,
        messages: List<AirbyteMessage>,
        defaultSchema: String?
    )
    fun implementsOverwrite(): Boolean
    fun getProtocolVersion(): ProtocolVersion
    fun normalizationFromDefinition(): Boolean
    var processFactory: ProcessFactory
    fun getNormalizationImageName(): String?
    fun getNormalizationIntegrationType(): String?
    fun implementsAppend(): Boolean
    fun supportIncrementalSchemaChanges(): Boolean
    fun retrieveNormalizedRecords(
        catalog: AirbyteCatalog,
        defaultSchema: String?
    ): List<AirbyteRecordMessage>
    fun assertSameMessages(
        expected: List<AirbyteMessage>,
        actual: List<AirbyteRecordMessage>,
        pruneAirbyteInternalFields: Boolean
    )
    fun implementsAppendDedup(): Boolean
    fun supportsNormalization(): Boolean
    fun dbtFromDefinition(): Boolean
    var jobRoot: Path
    fun implementsNamespaces(): Boolean
    var testSchemas: HashSet<String>
    fun getNameTransformer(): Optional<NamingConventionTransformer>
    val imageName: String
    var testEnv: AbstractDestinationAcceptanceTest.TestDestinationEnv
    val useV2Fields: Boolean
    val supportsChangeCapture: Boolean
    val expectNumericTimestamps: Boolean
    val expectSchemalessObjectsCoercedToStrings: Boolean
    val expectUnionsPromotedToDisjointRecords: Boolean

    fun retrieveRecordsDataOnly(
        testEnv: AbstractDestinationAcceptanceTest.TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode>

    fun pruneAndMaybeFlatten(node: JsonNode): JsonNode

    fun checkTestCompatibility(
        testCompatibility: DataTypeTestArgumentProvider.TestCompatibility
    ): Boolean

    @Throws(Exception::class)
    fun runAndCheck(
        catalog: AirbyteCatalog,
        configuredCatalog: ConfiguredAirbyteCatalog,
        messages: List<AirbyteMessage>
    )

    /**
     * Override this method if the normalized namespace is different from the default one. E.g.
     * BigQuery does allow a name starting with a number. So it should change the expected
     * normalized namespace when testCaseId = "S3A-1". Find the testCaseId in
     * "namespace_test_cases.json".
     */
    open fun assertNamespaceNormalization(
        testCaseId: String?,
        expectedNormalizedNamespace: String?,
        actualNormalizedNamespace: String?
    )

    /** Whether the destination should be tested against different namespaces. */
    fun supportNamespaceTest(): Boolean

    /**
     * Function that returns all of the records in destination as json at the time this method is
     * invoked. These will be used to check that the data actually written is what should actually
     * be there. Note: this returns a set and does not test any order guarantees.
     *
     * @param testEnv
     * - information about the test environment.
     * @param streamName
     * - name of the stream for which we are retrieving records.
     * @param namespace
     * - the destination namespace records are located in. Null if not applicable. Usually a JDBC
     * schema.
     * @param streamSchema
     * - schema of the stream to be retrieved. This is only necessary for destinations in which data
     * types cannot be accurately inferred (e.g. in CSV destination, every value is a string).
     * @return All of the records in the destination at the time this method is invoked.
     * @throws Exception
     * - can throw any exception, test framework will handle.
     */
    @Throws(Exception::class)
    fun retrieveRecords(
        testEnv: AbstractDestinationAcceptanceTest.TestDestinationEnv?,
        streamName: String,
        namespace: String,
        streamSchema: JsonNode
    ): List<JsonNode>

    class NamespaceTestCaseProvider : ArgumentsProvider {
        @Throws(Exception::class)
        override fun provideArguments(context: ExtensionContext): Stream<out Arguments> {
            val testCases = Jsons.deserialize(MoreResources.readResource(NAMESPACE_TEST_CASES_JSON))
            return MoreIterators.toList(testCases.elements())
                .filter { testCase: JsonNode -> testCase["enabled"].asBoolean() }
                .map { testCase: JsonNode ->
                    val namespaceInCatalog =
                        TestingNamespaces.generate(testCase["namespace"].asText())
                    val namespaceInDst =
                        TestingNamespaces.generateFromOriginal(
                            namespaceInCatalog,
                            testCase["namespace"].asText(),
                            testCase["normalized"].asText()
                        )
                    Arguments.of(
                        testCase["id"]
                            .asText(), // Add uniqueness to namespace to avoid collisions between
                        // tests.
                        namespaceInCatalog,
                        namespaceInDst
                    )
                }
                .stream()
        }

        companion object {
            const val NAMESPACE_TEST_CASES_JSON: String = "namespace_test_cases.json"
        }
    }

    companion object {
        @JvmStatic
        val JOB_ID = "0"
        @JvmStatic
        val JOB_ATTEMPT = 0

        /** Mutate the input airbyte record message namespace. */
        @JvmStatic
        fun getRecordMessagesWithNewNamespace(
            airbyteMessages: List<AirbyteMessage>,
            namespace: String?
        ): List<AirbyteMessage> {
            airbyteMessages.forEach(
                Consumer { message: AirbyteMessage ->
                    if (message.record != null) {
                        message.record.namespace = namespace
                    }
                }
            )
            return airbyteMessages
        }

        @JvmStatic
        public fun <V0, V1> convertProtocolObject(v1: V1, klass: Class<V0>): V0 {
            return Jsons.`object`(Jsons.jsonNode(v1), klass)!!
        }

        @JvmStatic
        @Throws(IOException::class)
        fun readCatalogFromFile(catalogFilename: String): AirbyteCatalog {
            return Jsons.deserialize(
                MoreResources.readResource(catalogFilename),
                AirbyteCatalog::class.java
            )
        }

        @JvmStatic
        @Throws(IOException::class)
        fun readMessagesFromFile(messagesFilename: String): List<AirbyteMessage> {
            return MoreResources.readResource(messagesFilename).trim().lines().map {
                Jsons.deserialize(it, AirbyteMessage::class.java)
            }
        }

        @JvmStatic
        val specialNumericTypesSupportTest: AbstractDestinationAcceptanceTest.SpecialNumericTypes
            /**
             * NaN and Infinity test are not supported by default. Please override this method to
             * specify NaN/Infinity types support example:
             *
             * <pre>
             *
             * protected SpecialNumericTypes getSpecialNumericTypesSupportTest() { return
             * SpecialNumericTypes.builder() .supportNumberNan(true) .supportIntegerNan(true)
             * .build(); } </pre> *
             *
             * @return SpecialNumericTypes with support flags
             */
            get() = AbstractDestinationAcceptanceTest.SpecialNumericTypes()
    }
}
