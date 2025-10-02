/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.destination.motherduck.write

import io.airbyte.cdk.command.ConfigurationSpecification
import io.airbyte.cdk.load.command.DestinationStream
import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.NullValue
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.test.util.DestinationCleaner
import io.airbyte.cdk.load.test.util.DestinationDataDumper
import io.airbyte.cdk.load.test.util.ExpectedRecordMapper
import io.airbyte.cdk.load.test.util.OutputRecord
import io.airbyte.cdk.load.write.BasicFunctionalityIntegrationTest
import io.airbyte.cdk.load.write.DedupBehavior
import io.airbyte.cdk.load.write.SchematizedNestedValueBehavior
import io.airbyte.cdk.load.write.StronglyTyped
import io.airbyte.cdk.load.write.UnionBehavior
import io.airbyte.integrations.destination.motherduck.spec.MotherDuckConfiguration
import io.airbyte.integrations.destination.motherduck.spec.MotherDuckConfigurationFactory
import io.airbyte.integrations.destination.motherduck.spec.MotherDuckSpecification
import java.nio.file.Path
import java.nio.file.Paths

internal val CONFIG_PATH: Path = Paths.get("secrets/config.json")

class MotherDuckAcceptanceTest :
    BasicFunctionalityIntegrationTest(
        configContents = """
            {
                "motherduck_api_key": "",
                "destination_path": ":memory:",
                "schema": "main"
            }
        """.trimIndent(),
        configSpecClass = MotherDuckSpecification::class.java,
        dataDumper = MotherDuckDataDumper { spec ->
            MotherDuckConfigurationFactory().make(spec as MotherDuckSpecification)
        },
        destinationCleaner = MotherDuckDataCleaner,
        isStreamSchemaRetroactive = true,
        dedupBehavior = DedupBehavior(DedupBehavior.CdcDeletionMode.HARD_DELETE),
        stringifySchemalessObjects = true,
        schematizedObjectBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        schematizedArrayBehavior = SchematizedNestedValueBehavior.PASS_THROUGH,
        unionBehavior = UnionBehavior.PASS_THROUGH,
        supportFileTransfer = false,
        commitDataIncrementally = false,
        allTypesBehavior =
            StronglyTyped(
                integerCanBeLarge = true,
                numberCanBeLarge = true,
                nestedFloatLosesPrecision = false,
            ),
        recordMangler = MotherDuckExpectedRecordMapper,
    )

class MotherDuckDataDumper(
    private val configProvider: (ConfigurationSpecification) -> MotherDuckConfiguration
) : DestinationDataDumper {
    override fun dumpRecords(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): List<OutputRecord> {
        val config = configProvider(spec)
        val dataSource = MotherDuckTestUtils.createDuckDBDataSource(config)
        val output = mutableListOf<OutputRecord>()

        dataSource.use { ds ->
            ds.connection.use { connection ->
                val statement = connection.createStatement()
                val tableName = "${config.schema}.${stream.mappedDescriptor.name}"

                val tableExistsQuery = """
                    SELECT COUNT(*) as count
                    FROM information_schema.tables
                    WHERE table_schema = '${config.schema}'
                    AND table_name = '${stream.mappedDescriptor.name}'
                """.trimIndent()

                val existsResultSet = statement.executeQuery(tableExistsQuery)
                existsResultSet.next()
                val tableExists = existsResultSet.getInt("count") > 0
                existsResultSet.close()

                if (!tableExists) {
                    return output
                }

                val resultSet = statement.executeQuery("SELECT * FROM $tableName")

                while (resultSet.next()) {
                    val dataMap = linkedMapOf<String, AirbyteValue>()
                    for (i in 1..resultSet.metaData.columnCount) {
                        val columnName = resultSet.metaData.getColumnName(i)
                        if (!Meta.COLUMN_NAMES.contains(columnName)) {
                            val value = resultSet.getObject(i)
                            dataMap[columnName] = value?.let { AirbyteValue.from(it) } ?: NullValue
                        }
                    }
                    val outputRecord = OutputRecord(
                        rawId = resultSet.getString(Meta.COLUMN_NAME_AB_RAW_ID),
                        extractedAt = resultSet.getTimestamp(Meta.COLUMN_NAME_AB_EXTRACTED_AT).toInstant().toEpochMilli(),
                        loadedAt = null,
                        generationId = resultSet.getLong(Meta.COLUMN_NAME_AB_GENERATION_ID),
                        data = ObjectValue(dataMap),
                        airbyteMeta = null
                    )
                    output.add(outputRecord)
                }
            }
        }
        return output
    }

    override fun dumpFile(
        spec: ConfigurationSpecification,
        stream: DestinationStream
    ): Map<String, String> {
        throw UnsupportedOperationException("MotherDuck does not support file transfer.")
    }
}

object MotherDuckDataCleaner : DestinationCleaner {
    override fun cleanup() {
    }
}

object MotherDuckExpectedRecordMapper : ExpectedRecordMapper {
    override fun mapRecord(expectedRecord: OutputRecord, schema: AirbyteType): OutputRecord = expectedRecord
}
