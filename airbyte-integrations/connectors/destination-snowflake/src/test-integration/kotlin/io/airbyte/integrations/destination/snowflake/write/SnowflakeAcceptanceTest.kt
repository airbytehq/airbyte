/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import com.fasterxml.jackson.databind.node.ObjectNode
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.NameMapper
import io.airbyte.cdk.load.test.util.NoopNameMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.util.serializeToString
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.ColumnDropBehavior
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.CONFIG_WITH_AUTH_STAGING
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.CONFIG_WITH_AUTH_STAGING_AND_RAW_OVERRIDE
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.CONFIG_WITH_AUTH_STAGING_IGNORE_CASING
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.getConfigPath
import io.airbyte.integrations.destination.snowflake.spec.NumberDataType
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeConfigurationFactory
import io.airbyte.integrations.destination.snowflake.spec.SnowflakeSpecification
import io.airbyte.protocol.models.v0.AirbyteRecordMessageMetaChange
import java.nio.file.Files
import java.nio.file.Path
import org.junit.jupiter.api.Disabled
import org.junit.jupiter.api.Test

internal val CONFIG_PATH = getConfigPath(CONFIG_WITH_AUTH_STAGING)
internal val CONFIG_IGNORE_CASING_PATH = getConfigPath(CONFIG_WITH_AUTH_STAGING_IGNORE_CASING)
internal val RAW_CONFIG_PATH = getConfigPath(CONFIG_WITH_AUTH_STAGING_AND_RAW_OVERRIDE)

// Add number_data_type toggle to the config path.
internal val NUMBER_38_9_CONFIG: String by lazy {
    (Jsons.readTree(Files.readString(CONFIG_PATH)) as ObjectNode)
        .apply { put("number_data_type", "NUMBER(38,9)") }
        .serializeToString()
}

/*
 * SnowflakeInsertAcceptanceTest runs the full BasicFunctionalityIntegrationTest suite. Every other
 * variant in this file exists to cover a single configuration or input-medium dimension, and only
 * runs the tests whose behavior depends on that dimension; the rest of the suite is disabled with
 * one of the reasons below, since it would exercise exactly the same code paths as
 * SnowflakeInsertAcceptanceTest.
 */
private const val MEDIUM_INDEPENDENT =
    "Does not depend on the input medium/format; covered by SnowflakeInsertAcceptanceTest"
private const val CASING_INDEPENDENT =
    "Does not depend on QUOTED_IDENTIFIERS_IGNORE_CASE; covered by SnowflakeInsertAcceptanceTest"
private const val NUMBER_TYPE_INDEPENDENT =
    "Does not depend on number_data_type; covered by SnowflakeInsertAcceptanceTest"
private const val RAW_PROTO_LIFECYCLE_COVERED =
    "Sync lifecycle over sockets is covered by SnowflakeInsertProtoAcceptanceTest, raw-mode table " +
        "management by SnowflakeRawInsertAcceptanceTest"

/** Default config over STDIO/JSONL. The only variant that runs the full suite. */
class SnowflakeInsertAcceptanceTest :
    SnowflakeAcceptanceTest(
        configPath = CONFIG_PATH,
        dataDumper =
            SnowflakeDataDumper { spec ->
                SnowflakeConfigurationFactory().make(spec as SnowflakeSpecification)
            },
        recordMapper = SnowflakeExpectedRecordMapper(),
        nameMapper = SnowflakeNameMapper(),
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    ) {
    @Test
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }
}

/**
 * Covers the `QUOTED_IDENTIFIERS_IGNORE_CASE=true` account parameter (see
 * [CONFIG_WITH_AUTH_STAGING_IGNORE_CASING]), which upcases identifiers regardless of quoting. Only
 * the tests that exercise identifier handling run here: creating/describing/altering tables,
 * non-trivial stream and column names, MERGE, and generation-id lookups.
 */
class SnowflakeInsertIgnoreCasingAcceptanceTest :
    SnowflakeAcceptanceTest(
        configPath = CONFIG_IGNORE_CASING_PATH,
        dataDumper =
            SnowflakeDataDumper { spec ->
                SnowflakeConfigurationFactory().make(spec as SnowflakeSpecification)
            },
        recordMapper = SnowflakeExpectedRecordMapper(),
        nameMapper = SnowflakeNameMapper(),
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }

    @Disabled(CASING_INDEPENDENT)
    @Test
    override fun testMidSyncCheckpointingStreamState() = super.testMidSyncCheckpointingStreamState()

    @Disabled(CASING_INDEPENDENT)
    @Test
    override fun testTruncateRefreshChangeSyncMode() = super.testTruncateRefreshChangeSyncMode()

    @Disabled(CASING_INDEPENDENT)
    @Test
    override fun testInterruptedTruncateWithPriorData() =
        super.testInterruptedTruncateWithPriorData()

    @Disabled(CASING_INDEPENDENT)
    @Test
    override fun testInterruptedTruncateWithoutPriorData() =
        super.testInterruptedTruncateWithoutPriorData()

    @Disabled(CASING_INDEPENDENT) @Test override fun testAppend() = super.testAppend()

    @Disabled(CASING_INDEPENDENT)
    @Test
    override fun testAppendJsonSchemaEvolution() = super.testAppendJsonSchemaEvolution()

    @Disabled(CASING_INDEPENDENT)
    @Test
    override fun testDedupWithStringKey() = super.testDedupWithStringKey()

    @Disabled(CASING_INDEPENDENT) @Test override fun testDedupNoCursor() = super.testDedupNoCursor()

    @Disabled(CASING_INDEPENDENT)
    @Test
    override fun testDedupChangeCursor() = super.testDedupChangeCursor()

    @Disabled(CASING_INDEPENDENT) @Test override fun testDedupChangePk() = super.testDedupChangePk()

    @Disabled(CASING_INDEPENDENT)
    @Test
    override fun testManyStreamsCompletion() = super.testManyStreamsCompletion()

    @Disabled(CASING_INDEPENDENT) @Test override fun testBasicTypes() = super.testBasicTypes()

    @Disabled(CASING_INDEPENDENT)
    @Test
    override fun testContainerTypes() = super.testContainerTypes()

    @Disabled(CASING_INDEPENDENT) @Test override fun testUnknownTypes() = super.testUnknownTypes()

    @Disabled(CASING_INDEPENDENT) @Test override fun testUnions() = super.testUnions()

    @Disabled(CASING_INDEPENDENT) @Test override fun testNoColumns() = super.testNoColumns()

    @Disabled(CASING_INDEPENDENT) @Test override fun testNoData() = super.testNoData()

    @Disabled(CASING_INDEPENDENT)
    @Test
    override fun testTruncateRefreshNoData() = super.testTruncateRefreshNoData()

    @Disabled(CASING_INDEPENDENT) @Test override fun testClear() = super.testClear()
}

/** Default config over SOCKET/PROTOBUF. See [SnowflakeProtoAcceptanceTest] for the scope. */
class SnowflakeInsertProtoAcceptanceTest :
    SnowflakeProtoAcceptanceTest(
        configPath = CONFIG_PATH,
        dataDumper =
            SnowflakeDataDumper { spec ->
                SnowflakeConfigurationFactory().make(spec as SnowflakeSpecification)
            },
        recordMapper = SnowflakeExpectedRecordMapper(),
        nameMapper = SnowflakeNameMapper(),
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

/**
 * Covers `number_data_type = NUMBER(38,9)` (the default is FLOAT). [testNumericTypes] and
 * [testBasicTypes] are the only tests that write NUMBER columns, so only those run here.
 */
class SnowflakeNumberWithScaleInsertAcceptanceTest :
    SnowflakeAcceptanceTest(
        configPath = CONFIG_PATH,
        configContents = NUMBER_38_9_CONFIG,
        dataDumper =
            SnowflakeDataDumper { spec ->
                SnowflakeConfigurationFactory().make(spec as SnowflakeSpecification)
            },
        recordMapper = SnowflakeExpectedRecordMapper(NumberDataType.NUMBER_38_9),
        nameMapper = SnowflakeNameMapper(),
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = true,
                // NUMBER(38,9) holds at most 29 digits left of the decimal point.
                numberCanBeLarge = false,
                nestedFloatLosesPrecision = false,
                numberIsFixedPointPrecision38Scale9 = true,
            ),
    ) {
    @Test
    override fun testNumericTypes() {
        super.testNumericTypes()
    }

    @Disabled(NUMBER_TYPE_INDEPENDENT) @Test override fun testBasicWrite() = super.testBasicWrite()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testMidSyncCheckpointingStreamState() = super.testMidSyncCheckpointingStreamState()

    @Disabled(NUMBER_TYPE_INDEPENDENT) @Test override fun testNamespaces() = super.testNamespaces()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testFunkyCharacters() = super.testFunkyCharacters()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testFunkyCharactersDedup() = super.testFunkyCharactersDedup()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testTruncateRefresh() = super.testTruncateRefresh()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testTruncateRefreshChangeSyncMode() = super.testTruncateRefreshChangeSyncMode()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testInterruptedTruncateWithPriorData() =
        super.testInterruptedTruncateWithPriorData()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testInterruptedTruncateWithoutPriorData() =
        super.testInterruptedTruncateWithoutPriorData()

    @Disabled(NUMBER_TYPE_INDEPENDENT) @Test override fun testAppend() = super.testAppend()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testAppendSchemaEvolution() = super.testAppendSchemaEvolution()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testAppendJsonSchemaEvolution() = super.testAppendJsonSchemaEvolution()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testOverwriteSchemaEvolution() = super.testOverwriteSchemaEvolution()

    @Disabled(NUMBER_TYPE_INDEPENDENT) @Test override fun testDedup() = super.testDedup()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testDedupWithStringKey() = super.testDedupWithStringKey()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testDedupNoCursor() = super.testDedupNoCursor()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testDedupChangeCursor() = super.testDedupChangeCursor()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testDedupChangePk() = super.testDedupChangePk()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testManyStreamsCompletion() = super.testManyStreamsCompletion()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testContainerTypes() = super.testContainerTypes()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testUnknownTypes() = super.testUnknownTypes()

    @Disabled(NUMBER_TYPE_INDEPENDENT) @Test override fun testUnions() = super.testUnions()

    @Disabled(NUMBER_TYPE_INDEPENDENT) @Test override fun testNoColumns() = super.testNoColumns()

    @Disabled(NUMBER_TYPE_INDEPENDENT) @Test override fun testNoData() = super.testNoData()

    @Disabled(NUMBER_TYPE_INDEPENDENT)
    @Test
    override fun testTruncateRefreshNoData() = super.testTruncateRefreshNoData()

    @Disabled(NUMBER_TYPE_INDEPENDENT) @Test override fun testClear() = super.testClear()
}

/**
 * Covers legacy raw-tables mode (`disable_type_dedupe`) over STDIO/JSONL. Runs every test that
 * applies to raw mode, since this is the only full-suite coverage of that write path.
 */
class SnowflakeRawInsertAcceptanceTest :
    SnowflakeAcceptanceTest(
        configPath = RAW_CONFIG_PATH,
        dataDumper =
            SnowflakeRawDataDumper { spec ->
                SnowflakeConfigurationFactory().make(spec as SnowflakeSpecification)
            },
        recordMapper = SnowflakeExpectedRawRecordMapper,
        nameMapper = NoopNameMapper,
        isStreamSchemaRetroactive = false,
        dedupBehavior = null,
        nullEqualsUnset = false,
        coercesLegacyUnions = false,
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    ) {
    @Test
    override fun testFunkyCharacters() {
        super.testFunkyCharacters()
    }
}

/**
 * Legacy raw-tables mode over SOCKET/PROTOBUF. On top of the [SnowflakeProtoAcceptanceTest] scope,
 * this only keeps the tests that exercise proto-to-JSON re-serialization into `_airbyte_data`.
 */
class SnowflakeRawInsertProtoAcceptanceTest :
    SnowflakeProtoAcceptanceTest(
        configPath = RAW_CONFIG_PATH,
        dataDumper =
            SnowflakeRawDataDumper { spec ->
                SnowflakeConfigurationFactory().make(spec as SnowflakeSpecification)
            },
        recordMapper = SnowflakeExpectedRawRecordMapper,
        nameMapper = NoopNameMapper,
        isStreamSchemaRetroactive = false,
        dedupBehavior = null,
        nullEqualsUnset = false,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }

    @Disabled("https://github.com/airbytehq/airbyte-internal-issues/issues/15495")
    @Test
    override fun testContainerTypes() {
        super.testContainerTypes()
    }

    @Disabled(RAW_PROTO_LIFECYCLE_COVERED)
    @Test
    override fun testMidSyncCheckpointingStreamState() = super.testMidSyncCheckpointingStreamState()

    @Disabled(RAW_PROTO_LIFECYCLE_COVERED)
    @Test
    override fun testInterruptedTruncateWithPriorData() =
        super.testInterruptedTruncateWithPriorData()

    @Disabled(RAW_PROTO_LIFECYCLE_COVERED)
    @Test
    override fun testManyStreamsCompletion() = super.testManyStreamsCompletion()
}

abstract class SnowflakeAcceptanceTest(
    configPath: Path,
    configContents: String = Files.readString(configPath),
    dataChannelMedium: DataChannelMedium = DataChannelMedium.STDIO,
    dataChannelFormat: DataChannelFormat = DataChannelFormat.JSONL,
    dataDumper: DestinationDataDumper,
    recordMapper: ExpectedRecordMapper,
    nameMapper: NameMapper,
    isStreamSchemaRetroactive: Boolean = true,
    isStreamSchemaRetroactiveForUnknownTypeToString: Boolean = true,
    dedupBehavior: DedupBehavior? = DedupBehavior(DedupBehavior.CdcDeletionMode.HARD_DELETE),
    nullEqualsUnset: Boolean = true,
    coercesLegacyUnions: Boolean = false,
    unknownTypesBehavior: UnknownTypesBehavior,
    allTypesBehavior: StronglyTyped =
        StronglyTyped(
            integerCanBeLarge = true,
            numberCanBeLarge = true,
            nestedFloatLosesPrecision = false,
        ),
) :
    BasicFunctionalityIntegrationTest(
        configContents = configContents,
        configSpecClass = SnowflakeSpecification::class.java,
        dataDumper = dataDumper,
        destinationCleaner = SnowflakeDataCleaner,
        isStreamSchemaRetroactive = isStreamSchemaRetroactive,
        isStreamSchemaRetroactiveForUnknownTypeToString =
            isStreamSchemaRetroactiveForUnknownTypeToString,
        dedupBehavior = dedupBehavior,
        stringifySchemalessObjects = false,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        stringifyUnionObjects = false,
        commitDataIncrementally = false,
        commitDataIncrementallyOnAppend = false,
        commitDataIncrementallyToEmptyDestinationOnAppend = true,
        commitDataIncrementallyToEmptyDestinationOnDedupe = false,
        allTypesBehavior = allTypesBehavior,
        unknownTypesBehavior = unknownTypesBehavior,
        nullEqualsUnset = nullEqualsUnset,
        dedupChangeUsesDefault = false,
        columnDropBehavior = ColumnDropBehavior.RETAIN,
        testSpeedModeStatsEmission = true,
        configUpdater = SnowflakeMigrationConfigurationUpdater(),
        dataChannelMedium = dataChannelMedium,
        dataChannelFormat = dataChannelFormat,
        mismatchedTypesUnrepresentable = false,
        recordMangler = recordMapper,
        nameMapper = nameMapper,
        coercesLegacyUnions = coercesLegacyUnions,
    )

/**
 * Base class for the SOCKET/PROTOBUF variants. The connector sees the same records regardless of
 * the wire format, so these variants only run the tests whose behavior depends on the input medium:
 * state handling, checkpointing, stream completion/interruption, and value decoding (proto renders
 * unknown types as NULL). Table management is covered by the STDIO/JSONL classes.
 */
abstract class SnowflakeProtoAcceptanceTest(
    configPath: Path,
    dataDumper: DestinationDataDumper,
    recordMapper: ExpectedRecordMapper,
    nameMapper: NameMapper,
    isStreamSchemaRetroactive: Boolean = true,
    dedupBehavior: DedupBehavior? = DedupBehavior(DedupBehavior.CdcDeletionMode.HARD_DELETE),
    nullEqualsUnset: Boolean = true,
) :
    SnowflakeAcceptanceTest(
        configPath = configPath,
        dataDumper = dataDumper,
        recordMapper = recordMapper,
        nameMapper = nameMapper,
        isStreamSchemaRetroactive = isStreamSchemaRetroactive,
        isStreamSchemaRetroactiveForUnknownTypeToString = false,
        dedupBehavior = dedupBehavior,
        nullEqualsUnset = nullEqualsUnset,
        dataChannelFormat = DataChannelFormat.PROTOBUF,
        dataChannelMedium = DataChannelMedium.SOCKET,
        unknownTypesBehavior = UnknownTypesBehavior.NULL,
    ) {
    @Disabled(MEDIUM_INDEPENDENT) @Test override fun testNamespaces() = super.testNamespaces()

    @Disabled(MEDIUM_INDEPENDENT)
    @Test
    override fun testFunkyCharacters() = super.testFunkyCharacters()

    @Disabled(MEDIUM_INDEPENDENT)
    @Test
    override fun testFunkyCharactersDedup() = super.testFunkyCharactersDedup()

    @Disabled(MEDIUM_INDEPENDENT)
    @Test
    override fun testTruncateRefresh() = super.testTruncateRefresh()

    @Disabled(MEDIUM_INDEPENDENT)
    @Test
    override fun testTruncateRefreshChangeSyncMode() = super.testTruncateRefreshChangeSyncMode()

    @Disabled(MEDIUM_INDEPENDENT)
    @Test
    override fun testInterruptedTruncateWithoutPriorData() =
        super.testInterruptedTruncateWithoutPriorData()

    @Disabled(MEDIUM_INDEPENDENT) @Test override fun testAppend() = super.testAppend()

    @Disabled(MEDIUM_INDEPENDENT)
    @Test
    override fun testAppendSchemaEvolution() = super.testAppendSchemaEvolution()

    @Disabled(MEDIUM_INDEPENDENT)
    @Test
    override fun testOverwriteSchemaEvolution() = super.testOverwriteSchemaEvolution()

    @Disabled(MEDIUM_INDEPENDENT)
    @Test
    override fun testDedupWithStringKey() = super.testDedupWithStringKey()

    @Disabled(MEDIUM_INDEPENDENT) @Test override fun testDedupNoCursor() = super.testDedupNoCursor()

    @Disabled(MEDIUM_INDEPENDENT)
    @Test
    override fun testDedupChangeCursor() = super.testDedupChangeCursor()

    @Disabled(MEDIUM_INDEPENDENT) @Test override fun testDedupChangePk() = super.testDedupChangePk()

    @Disabled(MEDIUM_INDEPENDENT) @Test override fun testNoColumns() = super.testNoColumns()

    @Disabled(MEDIUM_INDEPENDENT) @Test override fun testNoData() = super.testNoData()

    @Disabled(MEDIUM_INDEPENDENT)
    @Test
    override fun testTruncateRefreshNoData() = super.testTruncateRefreshNoData()

    @Disabled(MEDIUM_INDEPENDENT) @Test override fun testClear() = super.testClear()
}

fun stringToMeta(metaAsString: String?): OutputRecord.Meta? {
    if (metaAsString.isNullOrEmpty()) {
        return null
    }
    val metaJson = Jsons.readTree(metaAsString)

    val changes =
        (metaJson["changes"] as ArrayNode).map { change ->
            val changeNode = change as JsonNode
            Meta.Change(
                field = changeNode["field"].textValue().uppercase(),
                change =
                    AirbyteRecordMessageMetaChange.Change.fromValue(
                        changeNode["change"].textValue(),
                    ),
                reason =
                    AirbyteRecordMessageMetaChange.Reason.fromValue(
                        changeNode["reason"].textValue(),
                    ),
            )
        }

    return OutputRecord.Meta(
        changes = changes,
        syncId = metaJson["sync_id"].longValue(),
    )
}
