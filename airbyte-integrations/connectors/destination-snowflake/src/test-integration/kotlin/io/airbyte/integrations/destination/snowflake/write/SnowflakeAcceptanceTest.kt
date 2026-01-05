/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.snowflake.write

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.node.ArrayNode
import io.airbyte.cdk.load.config.DataChannelFormat
import io.airbyte.cdk.load.config.DataChannelMedium
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.NameMapper
import io.airbyte.cdk.load.test.util.NoopNameMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.util.Jsons
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.cdk.load.write.UnknownTypesBehavior
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.CONFIG_WITH_AUTH_STAGING
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.CONFIG_WITH_AUTH_STAGING_AND_RAW_OVERRIDE
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.CONFIG_WITH_AUTH_STAGING_IGNORE_CASING
import io.airbyte.integrations.destination.snowflake.SnowflakeTestUtils.getConfigPath
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

class SnowflakeInsertAcceptanceTest :
    SnowflakeAcceptanceTest(
        configPath = CONFIG_PATH,
        dataDumper =
            SnowflakeDataDumper { spec ->
                SnowflakeConfigurationFactory().make(spec as SnowflakeSpecification)
            },
        recordMapper = SnowflakeExpectedRecordMapper,
        nameMapper = SnowflakeNameMapper(),
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    ) {
    @Test
    override fun testAppendSchemaEvolution() {
        super.testAppendSchemaEvolution()
    }
}

class SnowflakeInsertIgnoreCasingAcceptanceTest :
    SnowflakeAcceptanceTest(
        configPath = CONFIG_IGNORE_CASING_PATH,
        dataDumper =
            SnowflakeDataDumper { spec ->
                SnowflakeConfigurationFactory().make(spec as SnowflakeSpecification)
            },
        recordMapper = SnowflakeExpectedRecordMapper,
        nameMapper = SnowflakeNameMapper(),
        unknownTypesBehavior = UnknownTypesBehavior.PASS_THROUGH,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

class SnowflakeInsertProtoAcceptanceTest :
    SnowflakeAcceptanceTest(
        configPath = CONFIG_PATH,
        dataDumper =
            SnowflakeDataDumper { spec ->
                SnowflakeConfigurationFactory().make(spec as SnowflakeSpecification)
            },
        recordMapper = SnowflakeExpectedRecordMapper,
        nameMapper = SnowflakeNameMapper(),
        dataChannelFormat = DataChannelFormat.PROTOBUF,
        dataChannelMedium = DataChannelMedium.SOCKET,
        unknownTypesBehavior = UnknownTypesBehavior.NULL,
        isStreamSchemaRetroactiveForUnknownTypeToString = false,
    ) {
    @Test
    override fun testBasicWrite() {
        super.testBasicWrite()
    }
}

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

class SnowflakeRawInsertProtoAcceptanceTest :
    SnowflakeAcceptanceTest(
        configPath = RAW_CONFIG_PATH,
        dataDumper =
            SnowflakeRawDataDumper { spec ->
                SnowflakeConfigurationFactory().make(spec as SnowflakeSpecification)
            },
        recordMapper = SnowflakeExpectedRawRecordMapper,
        nameMapper = NoopNameMapper,
        isStreamSchemaRetroactive = false,
        isStreamSchemaRetroactiveForUnknownTypeToString = false,
        dedupBehavior = null,
        nullEqualsUnset = false,
        coercesLegacyUnions = false,
        dataChannelFormat = DataChannelFormat.PROTOBUF,
        dataChannelMedium = DataChannelMedium.SOCKET,
        unknownTypesBehavior = UnknownTypesBehavior.NULL,
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
}

abstract class SnowflakeAcceptanceTest(
    configPath: Path,
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
) :
    BasicFunctionalityIntegrationTest(
        configContents = Files.readString(configPath),
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
        supportFileTransfer = false,
        commitDataIncrementally = false,
        commitDataIncrementallyOnAppend = false,
        commitDataIncrementallyToEmptyDestinationOnAppend = true,
        commitDataIncrementallyToEmptyDestinationOnDedupe = false,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = true,
                numberCanBeLarge = true,
                nestedFloatLosesPrecision = false,
            ),
        unknownTypesBehavior = unknownTypesBehavior,
        nullEqualsUnset = nullEqualsUnset,
        dedupChangeUsesDefault = false,
        testSpeedModeStatsEmission = true,
        configUpdater = SnowflakeMigrationConfigurationUpdater(),
        dataChannelMedium = dataChannelMedium,
        dataChannelFormat = dataChannelFormat,
        mismatchedTypesUnrepresentable = false,
        recordMangler = recordMapper,
        nameMapper = nameMapper,
        coercesLegacyUnions = coercesLegacyUnions,
        useDataFlowPipeline = true,
    )

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
                        changeNode["change"].textValue()
                    ),
                reason =
                    AirbyteRecordMessageMetaChange.Reason.fromValue(
                        changeNode["reason"].textValue()
                    ),
            )
        }

    return OutputRecord.Meta(
        changes = changes,
        syncId = metaJson["sync_id"].longValue(),
    )
}
