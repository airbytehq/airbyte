/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.command.ValidatedJsonUtils
import io.airbyte.cdk.load.command.DestinationCatalog
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.command.EnvVarConstants
import io.airbyte.cdk.load.command.Property
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.IntegerType
import io.airbyte.cdk.load.data.ObjectTypeWithoutSchema
import io.airbyte.cdk.load.data.StringType
import io.airbyte.cdk.load.data.TimeTypeWithTimezone
import io.airbyte.cdk.load.data.TimeTypeWithoutTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithTimezone
import io.airbyte.cdk.load.data.TimestampTypeWithoutTimezone
import io.airbyte.cdk.load.message.DestinationRecordStreamComplete
import io.airbyte.cdk.load.test.util.ConfigurationUpdater
import io.airbyte.cdk.load.test.util.FakeConfigurationUpdater
import io.airbyte.cdk.load.test.util.IntegrationTest
import io.airbyte.cdk.load.test.util.IntegrationTest.Companion.defaultMicronautProperties
import io.airbyte.cdk.load.test.util.destination_process.DestinationProcess
import io.airbyte.cdk.load.test.util.destination_process.DestinationProcessFactory
import io.airbyte.protocol.models.Jsons
import io.github.oshai.kotlinlogging.KotlinLogging
import java.time.Instant
import java.time.LocalDateTime
import java.time.LocalTime
import java.time.OffsetDateTime
import java.time.ZoneOffset
import java.time.format.DateTimeFormatter
import kotlin.time.measureTime
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import org.apache.commons.lang3.RandomStringUtils
import org.junit.jupiter.api.BeforeAll
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestInfo
import org.junit.jupiter.api.extension.ExtendWith
import uk.org.webcompere.systemstubs.environment.EnvironmentVariables
import uk.org.webcompere.systemstubs.jupiter.SystemStub
import uk.org.webcompere.systemstubs.jupiter.SystemStubsExtension

private val log = KotlinLogging.logger {}

data class NamedField(val name: String, val type: AirbyteType, val sample: Any)

/** Defines a performance test scenario. */
interface PerformanceTestScenario {
    data class Summary(
        val records: Long,
        val size: Long,
        val expectedRecordsCount: Long,
    )

    /** The catalog used for the performance test. */
    val catalog: DestinationCatalog

    /**
     * The main method from the performance scenario.
     *
     * This would be where records are emitted to the destination. How, is up to the scenario to
     * define.
     */
    fun send(destination: DestinationProcess)

    /**
     * Returns the expectations from the test scenario: how many records were emitted, how many
     * records are expected to be written in the final table (in the case of duplicates, this should
     * be the number of distinct records) and the volume of data emitted.
     */
    fun getSummary(): Summary
}

/** Interface to implement for destination that support data validation. */
interface DataValidator {
    /**
     * Returns the count of how many records are present for the stream in the final table. null if
     * not found.
     */
    fun count(spec: ConfigurationSpecification, stream: DestinationStream): Long?
}

data class PerformanceTestSummary(
    val namespace: String?,
    val streamName: String,
    val recordCount: Long?,
    val emittedRecordCount: Long,
    val recordPerSeconds: Double,
    val megabytePerSeconds: Double,
)

typealias ValidationFunction = (List<PerformanceTestSummary>) -> Unit

@Suppress("SameParameterValue")
@ExtendWith(SystemStubsExtension::class)
abstract class BasicPerformanceTest(
    val defaultRecordsToInsert: Long,
    val configContents: String,
    val configSpecClass: Class<out ConfigurationSpecification>,
    val configUpdater: ConfigurationUpdater = FakeConfigurationUpdater,
    val dataValidator: DataValidator? = null,
    val micronautProperties: Map<Property, String> = emptyMap(),
) {

    protected val destinationProcessFactory = DestinationProcessFactory.get(emptyList())

    private lateinit var testInfo: TestInfo
    private lateinit var testPrettyName: String

    val randomizedNamespace = run {
        val randomSuffix = RandomStringUtils.secure().nextAlphabetic(4)
        val randomizedNamespaceDateFormatter = DateTimeFormatter.ofPattern("yyyyMMdd")
        val timestampString =
            LocalDateTime.ofInstant(Instant.now(), ZoneOffset.UTC)
                .format(randomizedNamespaceDateFormatter)
        "test$timestampString$randomSuffix"
    }

    val idColumn = NamedField("id", IntegerType, 1337)
    val twoStringColumns =
        listOf(
            NamedField("column1", StringType, "1".repeat(100)),
            NamedField("column2", StringType, "2".repeat(100)),
        )

    @Test
    open fun testInsertRecords() {
        testInsertRecords(null)
    }

    protected fun testInsertRecords(validation: ValidationFunction?) {
        runSync(
            testScenario =
                SingleStreamInsert(
                    idColumn = idColumn,
                    columns = twoStringColumns,
                    recordsToInsert = defaultRecordsToInsert,
                    randomizedNamespace = randomizedNamespace,
                    streamName = testInfo.testMethod.get().name,
                ),
            validation = validation,
        )
    }

    @Test
    open fun testInsertRecordsComplexTypes() {
        testInsertRecordsComplexTypes(null)
    }

    protected fun testInsertRecordsComplexTypes(validation: ValidationFunction?) {
        runSync(
            testScenario =
                SingleStreamInsert(
                    idColumn = idColumn,
                    columns =
                        listOf(
                            NamedField(
                                "tWithTz",
                                TimeTypeWithTimezone,
                                LocalTime.now().atOffset(ZoneOffset.UTC).toString()
                            ),
                            NamedField("t", TimeTypeWithoutTimezone, LocalTime.now().toString()),
                            NamedField(
                                "tsWithTz",
                                TimestampTypeWithTimezone,
                                OffsetDateTime.now().toString()
                            ),
                            NamedField(
                                "ts",
                                TimestampTypeWithoutTimezone,
                                OffsetDateTime.now().toLocalDateTime().toString()
                            ),
                            NamedField(
                                "object",
                                ObjectTypeWithoutSchema,
                                Jsons.serialize(mapOf("object" to "value"))
                            )
                        ),
                    recordsToInsert = defaultRecordsToInsert,
                    randomizedNamespace = randomizedNamespace,
                    streamName = testInfo.testMethod.get().name,
                ),
            validation = validation,
        )
    }

    @Test
    open fun testInsertRecordsWithDedup() {
        testInsertRecordsWithDedup(null)
    }

    protected fun testInsertRecordsWithDedup(validation: ValidationFunction?) {
        runSync(
            testScenario =
                SingleStreamInsert(
                    idColumn = idColumn,
                    columns = twoStringColumns,
                    dedup = true,
                    duplicateChance = 0.25,
                    recordsToInsert = defaultRecordsToInsert,
                    randomizedNamespace = randomizedNamespace,
                    streamName = testInfo.testMethod.get().name,
                ),
            validation = validation,
        )
    }

    @Test
    open fun testInsertRecordsWithManyColumns() {
        testInsertRecordsWithManyColumns(null)
    }

    protected fun testInsertRecordsWithManyColumns(validation: ValidationFunction?) {
        runSync(
            testScenario =
                SingleStreamInsert(
                    idColumn = idColumn,
                    columns = (1..100).map { NamedField("column$it", StringType, "1".repeat(50)) },
                    recordsToInsert = defaultRecordsToInsert,
                    randomizedNamespace = randomizedNamespace,
                    streamName = testInfo.testMethod.get().name,
                ),
            validation = validation,
        )
    }

    @Test
    open fun testAppendRecordsWithDuplicates() {
        testAppendRecordsWithDuplicates(null)
    }

    protected fun testAppendRecordsWithDuplicates(validation: ValidationFunction?) {
        runSync(
            testScenario =
                SingleStreamInsert(
                    idColumn = idColumn,
                    columns = twoStringColumns,
                    dedup = false,
                    duplicateChance = 0.25,
                    recordsToInsert = defaultRecordsToInsert,
                    randomizedNamespace = randomizedNamespace,
                    streamName = testInfo.testMethod.get().name,
                ),
            validation = validation,
        )
    }

    companion object {
        // Connectors are calling System.getenv rather than using micronaut-y properties,
        // so we have to mock it out, instead of just setting more properties
        // inside NonDockerizedDestination.
        // This field has no effect on DockerizedDestination, which explicitly
        // sets env vars when invoking `docker run`.
        @SystemStub lateinit var nonDockerMockEnvVars: EnvironmentVariables

        @JvmStatic
        @BeforeAll
        fun beforeAll() {
            // NonDockerizedDestinations are hardcoded on IntegrationTest, not fixing for now.
            IntegrationTest.nonDockerMockEnvVars = nonDockerMockEnvVars
            IntegrationTest.nonDockerMockEnvVars.set("WORKER_JOB_ID", "0")
        }
    }

    @BeforeEach
    fun getTestInfo(testInfo: TestInfo) {
        this.testInfo = testInfo
        testPrettyName = "${testInfo.testClass.get().simpleName}.${testInfo.displayName}"
        destinationProcessFactory.testName = testPrettyName
    }

    protected fun runSync(
        testScenario: PerformanceTestScenario,
        useFileTransfer: Boolean = false,
        validation: ValidationFunction? = null,
    ): List<PerformanceTestSummary> {
        val fileTransferProperty =
            if (useFileTransfer) {
                mapOf(EnvVarConstants.FILE_TRANSFER_ENABLED to "true")
            } else {
                emptyMap()
            }
        val testConfig = configUpdater.update(configContents)
        val destination =
            destinationProcessFactory.createDestinationProcess(
                "write",
                testConfig,
                testScenario.catalog.asProtocolObject(),
                useFileTransfer = useFileTransfer,
                micronautProperties =
                    micronautProperties + fileTransferProperty,
            )

        val duration =
            runBlocking(Dispatchers.IO) {
                launch { destination.run() }

                measureTime {
                    testScenario.send(destination)
                    testScenario.catalog.streams.forEach {
                        destination.sendMessage(
                            DestinationRecordStreamComplete(
                                    it.descriptor,
                                    System.currentTimeMillis()
                                )
                                .asProtocolMessage()
                        )
                    }
                    destination.shutdown()
                }
            }

        val summary = testScenario.getSummary()
        val recordPerSeconds = summary.records.toDouble() / duration.inWholeMilliseconds * 1000
        val megabytePerSeconds =
            summary.size.toDouble() / 1000000 / duration.inWholeMilliseconds * 1000
        log.info { "$testPrettyName: loaded ${summary.records} records in $duration" }
        log.info { "$testPrettyName: loaded ${"%.2f".format(recordPerSeconds)} rps" }
        log.info { "$testPrettyName: loaded ${"%.2f".format(megabytePerSeconds)} MBps" }

        val recordCount =
            dataValidator?.let { validator ->
                val parsedConfig = ValidatedJsonUtils.parseOne(configSpecClass, testConfig)
                val recordCount = validator.count(parsedConfig, testScenario.catalog.streams[0])

                recordCount?.also {
                    log.info {
                        "$testPrettyName: table contains ${it} records" +
                            " (expected ${summary.expectedRecordsCount} records, " +
                            "emitted ${summary.records} records)"
                    }
                }
            }

        val performanceTestSummary =
            listOf(
                PerformanceTestSummary(
                    namespace = testScenario.catalog.streams[0].descriptor.namespace,
                    streamName = testScenario.catalog.streams[0].descriptor.name,
                    recordCount = recordCount,
                    emittedRecordCount = summary.records,
                    recordPerSeconds = recordPerSeconds,
                    megabytePerSeconds = megabytePerSeconds,
                )
            )
        validation?.let { it(performanceTestSummary) }
        return performanceTestSummary
    }
}
