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
    val size = "5gb"
    val runOldRawTablesFast = true
    val runOldRawTablesSlow = true
    val runNewTableNaive = true
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
        for (part in listOf(1, 2)) {
            destHandler.execute(
                Sql.separately(
                    """DROP INDEX IF EXISTS no_raw_tables_experiment.old_raw_table_${size}_part${part}_raw_id""",
                    """DROP INDEX IF EXISTS no_raw_tables_experiment.old_raw_table_${size}_part${part}_extracted_at""",
                    """DROP INDEX IF EXISTS no_raw_tables_experiment.old_raw_table_${size}_part${part}_loaded_at""",
                    """
                    UPDATE no_raw_tables_experiment.old_raw_table_${size}_part${part}
                        SET _airbyte_loaded_at = NULL
                        WHERE true
                    """.trimIndent(),
                    """CREATE INDEX old_raw_table_${size}_part${part}_raw_id ON no_raw_tables_experiment.old_raw_table_${size}_part${part}(_airbyte_raw_id)""",
                    """CREATE INDEX old_raw_table_${size}_part${part}_extracted_at ON no_raw_tables_experiment.old_raw_table_${size}_part${part}(_airbyte_extracted_at)""",
                    """CREATE INDEX old_raw_table_${size}_part${part}_loaded_at ON no_raw_tables_experiment.old_raw_table_${size}_part${part}(_airbyte_loaded_at, _airbyte_extracted_at)""",
                ),
            )
        }
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

    PrintWriter(FileOutputStream("/Users/edgao/code/airbyte/raw_table_experiments/generated_files/postgres_newstyle.sql")).use { out ->
        out.println("-- naive create table --------------------------------")
        out.printSql(getNewStyleCreateFinalTableQuery(size, optimized = false))

        repeat(10) { out.println() }
        out.println("""-- "naive" dedup query -------------------------------""")
        out.printSql(getNewStyleDedupingQuery(size, 1, optimized = false))

//        repeat(10) { out.println() }
//        out.println("-- optimized create table --------------------------------")
//        out.printSql(getNewStyleCreateFinalTableQuery(size, optimized = true))
//
//        repeat(10) { out.println() }
//        out.println("""-- "optimized" dedup query -------------------------------""")
//        out.println(getNewStyleDedupingQuery(size, 1, optimized = true))
    }

    if (runNewTableNaive) {
        destHandler.execute(getNewStyleCreateFinalTableQuery(size, optimized = false))
        logger.info { "Executing new-style naive deduping for $size dataset, part 1 (upsert to empty table)" }
        destHandler.execute(getNewStyleDedupingQuery(size, 1, optimized = false))
        logger.info { "Executing new-style naive deduping for $size dataset, part 2 (upsert to populated table)" }
        destHandler.execute(getNewStyleDedupingQuery(size, 2, optimized = false))
    }

//    if (runNewTableOptimized) {
//        destHandler.execute(getNewStyleCreateFinalTableQuery(size, optimized = true))
//        logger.info { "Executing new-style optimized deduping for $size dataset, part 1 (upsert to empty table)" }
//        destHandler.execute(getNewStyleDedupingQuery(size, 1, optimized = true))
//        logger.info { "Executing new-style optimized deduping for $size dataset, part 2 (upsert to populated table)" }
//        destHandler.execute(getNewStyleDedupingQuery(size, 2, optimized = true))
//    }
}

fun getNewStyleCreateFinalTableQuery(size: String, optimized: Boolean): Sql {
    if (optimized) {
        throw NotImplementedError("TODO do something")
    }
    return Sql.separately(
        "DROP TABLE IF EXISTS no_raw_tables_experiment.new_final_table_${size}",
        """
            create table "no_raw_tables_experiment"."new_final_table_${size}" (
              "_airbyte_raw_id" varchar(36) not null,
              "_airbyte_extracted_at" timestamp with time zone not null,
              "_airbyte_generation_id" bigint,
              "_airbyte_meta" jsonb not null,
              "primary_key" bigint,
              "cursor" timestamp,
              "string" varchar,
              "bool" boolean,
              "integer" bigint,
              "float" decimal(38, 9),
              "date" date,
              "ts_with_tz" timestamp with time zone,
              "ts_without_tz" timestamp,
              "time_with_tz" time with time zone,
              "time_no_tz" time,
              "array" jsonb,
              "json_object" jsonb
            );
        """.trimIndent()
    )
}

fun getNewStyleDedupingQuery(size: String, part: Int, optimized: Boolean): Sql {
    if (optimized) {
        throw NotImplementedError("TODO do something")
    }
    return Sql.transactionally(
        """
            insert into
              "no_raw_tables_experiment"."new_final_table_${size}" (
                "primary_key",
                "cursor",
                "string",
                "bool",
                "integer",
                "float",
                "date",
                "ts_with_tz",
                "ts_without_tz",
                "time_with_tz",
                "time_no_tz",
                "array",
                "json_object",
                "_airbyte_raw_id",
                "_airbyte_extracted_at",
                "_airbyte_generation_id",
                "_airbyte_meta"
              )
            with "numbered_rows" as (
              select
                *,
                row_number() over (partition by "primary_key" order by "cursor" desc NULLS LAST, "_airbyte_extracted_at" desc) as "row_number"
              from "no_raw_tables_experiment"."new_input_table_${size}_part${part}"
            )
            select
              "primary_key",
              "cursor",
              "string",
              "bool",
              "integer",
              "float",
              "date",
              "ts_with_tz",
              "ts_without_tz",
              "time_with_tz",
              "time_no_tz",
              "array",
              "json_object",
              "_airbyte_raw_id",
              "_airbyte_extracted_at",
              "_airbyte_generation_id",
              "_airbyte_meta"
            from "numbered_rows"
            where "row_number" = 1;
        """.trimIndent(),
        """
            delete from "no_raw_tables_experiment"."new_final_table_${size}"
            where
              "_airbyte_raw_id" in (
                select
                  "_airbyte_raw_id"
                from
                  (
                    select
                      "_airbyte_raw_id",
                      row_number() over (
                        partition by "primary_key"
                        order by
                          "cursor" desc NULLS LAST,
                          "_airbyte_extracted_at" desc
                      ) as "row_number"
                    from
                      "no_raw_tables_experiment"."new_final_table_${size}"
                  ) as "airbyte_ids"
                where
                  "row_number" <> 1
              );
        """.trimIndent(),
    )
}
