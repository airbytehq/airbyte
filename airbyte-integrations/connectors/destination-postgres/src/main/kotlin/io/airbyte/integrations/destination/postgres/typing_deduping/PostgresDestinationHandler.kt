/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.destination.postgres.typing_deduping

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.cdk.db.jdbc.DefaultJdbcDatabase
import io.airbyte.cdk.db.jdbc.JdbcDatabase
import io.airbyte.cdk.integrations.destination.jdbc.typing_deduping.JdbcDestinationHandler
import io.airbyte.commons.exceptions.ConfigErrorException
import io.airbyte.commons.json.Jsons
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteProtocolType
import io.airbyte.integrations.base.destination.typing_deduping.AirbyteType
import io.airbyte.integrations.base.destination.typing_deduping.Array
import io.airbyte.integrations.base.destination.typing_deduping.Sql
import io.airbyte.integrations.base.destination.typing_deduping.Struct
import io.airbyte.integrations.base.destination.typing_deduping.Union
import io.airbyte.integrations.base.destination.typing_deduping.UnsupportedOneOf
import io.airbyte.integrations.destination.postgres.PostgresDestination
import io.airbyte.integrations.destination.postgres.PostgresGenerationHandler
import io.airbyte.integrations.destination.postgres.PostgresSQLNameTransformer
import io.github.oshai.kotlinlogging.KotlinLogging
import java.io.FileOutputStream
import java.io.PrintWriter
import java.nio.file.Files
import java.nio.file.Path
import java.util.Optional
import org.jooq.SQLDialect

class PostgresDestinationHandler(
    databaseName: String?,
    jdbcDatabase: JdbcDatabase,
    rawTableSchema: String,
    generationHandler: PostgresGenerationHandler,
) :
    JdbcDestinationHandler<PostgresState>(
        databaseName,
        jdbcDatabase,
        rawTableSchema,
        SQLDialect.POSTGRES,
        generationHandler = generationHandler
    ) {
    override fun toJdbcTypeName(airbyteType: AirbyteType): String {
        // This is mostly identical to the postgres implementation, but swaps jsonb to super
        if (airbyteType is AirbyteProtocolType) {
            return toJdbcTypeName(airbyteType)
        }
        return when (airbyteType.typeName) {
            Struct.TYPE,
            UnsupportedOneOf.TYPE,
            Array.TYPE -> "jsonb"
            Union.TYPE -> toJdbcTypeName((airbyteType as Union).chooseType())
            else -> throw IllegalArgumentException("Unsupported AirbyteType: $airbyteType")
        }
    }

    override fun toDestinationState(json: JsonNode): PostgresState {
        return PostgresState(
            json.hasNonNull("needsSoftReset") && json["needsSoftReset"].asBoolean(),
            json.hasNonNull("isAirbyteMetaPresentInRaw") &&
                json["isAirbyteMetaPresentInRaw"].asBoolean(),
            json.hasNonNull("isAirbyteGenerationIdPresent") &&
                json["isAirbyteGenerationIdPresent"].asBoolean()
        )
    }

    override fun createNamespaces(schemas: Set<String>) {
        TODO("Not yet implemented")
    }

    private fun toJdbcTypeName(airbyteProtocolType: AirbyteProtocolType): String {
        return when (airbyteProtocolType) {
            AirbyteProtocolType.STRING -> "varchar"
            AirbyteProtocolType.NUMBER -> "numeric"
            AirbyteProtocolType.INTEGER -> "int8"
            AirbyteProtocolType.BOOLEAN -> "bool"
            AirbyteProtocolType.TIMESTAMP_WITH_TIMEZONE -> "timestamptz"
            AirbyteProtocolType.TIMESTAMP_WITHOUT_TIMEZONE -> "timestamp"
            AirbyteProtocolType.TIME_WITH_TIMEZONE -> "timetz"
            AirbyteProtocolType.TIME_WITHOUT_TIMEZONE -> "time"
            AirbyteProtocolType.DATE -> "date"
            AirbyteProtocolType.UNKNOWN -> "jsonb"
        }
    }

    override fun execute(sql: Sql) {
        try {
            super.execute(sql)
        } catch (e: Exception) {
            // executing the
            // DROP TABLE command.
            if (
                e.message!!.contains("ERROR: cannot drop table") &&
                    e.message!!.contains("because other objects depend on it")
            ) {
                throw ConfigErrorException(
                    "Failed to drop table without the CASCADE option. Consider changing the drop_cascade configuration parameter",
                    e
                )
            }
            throw e
        }
    }
}

private val logger = KotlinLogging.logger {}
/**
 * Assumes that the old_raw_table_5mb_part1/part2 + new_input_table_5mb_part1/part2 tables already exist.
 * Will drop+recreate the old_final_table_5mb / new_final_table_5mb tables as needed.
 */
fun main() {
    val size = "5mb"
    val runOldRawTablesFast = true
    val runOldRawTablesSlow = true
    val runNewTableNaive = false
    val runNewTableOptimized = false

    val config = Jsons.deserialize(Files.readString(Path.of("/Users/edgao/Desktop/postgres_raw_tables_experiment.json")))
    val generator = PostgresSqlGenerator(PostgresSQLNameTransformer(), cascadeDrop = true)
    val destHandler = PostgresDestinationHandler(
        databaseName = "postgres",
        DefaultJdbcDatabase(PostgresDestination().getDataSource(config)),
        rawTableSchema = "no_raw_tables_experiment",
        PostgresGenerationHandler(),
    )

    fun resetOldTypingDeduping() {
        // reset the raw tables (i.e. unset loaded_at)
        destHandler.execute(Sql.separately(
            """
                UPDATE no_raw_tables_experiment.old_raw_table_${size}_part1
                SET _airbyte_loaded_at = NULL
                WHERE true
            """.trimIndent(),
            """
                UPDATE no_raw_tables_experiment.old_raw_table_${size}_part2
                SET _airbyte_loaded_at = NULL
                WHERE true
            """.trimIndent(),
        ))
        // drop+recreate `old_final_table_${size}`
        // part=0 here b/c the part number doesn't matter (we don't need the raw tables yet)
        destHandler.execute(generator.createTable(getStreamConfig(size, 0), suffix = "", force = true))
    }

    if (runOldRawTablesFast) {
        resetOldTypingDeduping()
        logger.info { "Executing old-style fast T+D for $size dataset, part 1 (upsert to empty table)" }
        destHandler.execute(
            generator.updateTable(
                getStreamConfig(size, part = 1),
                finalSuffix = "",
                minRawTimestamp = Optional.empty(),
                useExpensiveSaferCasting = false,
            )
        )
        logger.info { "Executing old-style fast T+D for $size dataset, part 2 (upsert to populated table)" }
        destHandler.execute(
            generator.updateTable(
                getStreamConfig(size, part = 2),
                finalSuffix = "",
                minRawTimestamp = Optional.empty(),
                useExpensiveSaferCasting = false,
            )
        )
    }

    if (runOldRawTablesSlow) {
        resetOldTypingDeduping()
        logger.info { "Executing old-style slow T+D for $size dataset, part 1 (upsert to empty table)" }
        destHandler.execute(
            generator.updateTable(
                getStreamConfig(size, part = 1),
                finalSuffix = "",
                minRawTimestamp = Optional.empty(),
                useExpensiveSaferCasting = true,
            )
        )
        logger.info { "Executing old-style slow T+D for $size dataset, part 2 (upsert to populated table)" }
        destHandler.execute(
            generator.updateTable(
                getStreamConfig(size, part = 2),
                finalSuffix = "",
                minRawTimestamp = Optional.empty(),
                useExpensiveSaferCasting = true,
            )
        )
    }

//    PrintWriter(FileOutputStream("/Users/edgao/code/airbyte/raw_table_experiments/generated_files/postgres_newstyle.sql")).use { out ->
//        out.println("-- naive create table --------------------------------")
//        out.printSql(getNewStyleCreateFinalTableQuery(size, optimized = false))
//
//        repeat(10) { out.println() }
//        out.println("""-- "naive" dedup query -------------------------------""")
//        out.println(getNewStyleDedupingQuery(size, 1, optimized = false))
//
//        repeat(10) { out.println() }
//        out.println("-- optimized create table --------------------------------")
//        out.printSql(getNewStyleCreateFinalTableQuery(size, optimized = true))
//
//        repeat(10) { out.println() }
//        out.println("""-- "optimized" dedup query -------------------------------""")
//        out.println(getNewStyleDedupingQuery(size, 1, optimized = true))
//    }
//
//    if (runNewTableNaive) {
//        destHandler.execute(getNewStyleCreateFinalTableQuery(size, optimized = false))
//        logger.info { "Executing new-style naive deduping for $size dataset, part 1 (upsert to empty table)" }
//        destHandler.execute(Sql.of(getNewStyleDedupingQuery(size, 1, optimized = false)))
//        logger.info { "Executing new-style naive deduping for $size dataset, part 2 (upsert to populated table)" }
//        destHandler.execute(Sql.of(getNewStyleDedupingQuery(size, 2, optimized = false)))
//    }
//
//    if (runNewTableOptimized) {
//        destHandler.execute(getNewStyleCreateFinalTableQuery(size, optimized = true))
//        logger.info { "Executing new-style optimized deduping for $size dataset, part 1 (upsert to empty table)" }
//        destHandler.execute(Sql.of(getNewStyleDedupingQuery(size, 1, optimized = true)))
//        logger.info { "Executing new-style optimized deduping for $size dataset, part 2 (upsert to populated table)" }
//        destHandler.execute(Sql.of(getNewStyleDedupingQuery(size, 2, optimized = true)))
//    }
}
