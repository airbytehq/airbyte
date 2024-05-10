/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.integrations.base.destination.typing_deduping

import com.google.common.annotations.VisibleForTesting
import io.airbyte.cdk.integrations.base.AirbyteExceptionHandler.Companion.addStringForDeinterpolation
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.protocol.models.v0.ConfiguredAirbyteCatalog
import io.airbyte.protocol.models.v0.ConfiguredAirbyteStream
import java.util.Optional
import java.util.function.Consumer
import org.apache.commons.codec.digest.DigestUtils
import org.slf4j.Logger
import org.slf4j.LoggerFactory

class CatalogParser
@JvmOverloads
constructor(
    private val sqlGenerator: SqlGenerator,
    private val rawNamespace: String = JavaBaseConstants.DEFAULT_AIRBYTE_INTERNAL_NAMESPACE
) {
    fun parseCatalog(catalog: ConfiguredAirbyteCatalog): ParsedCatalog {
        // this code is bad and I feel bad
        // it's mostly a port of the old normalization logic to prevent tablename collisions.
        // tbh I have no idea if it works correctly.
        val streamConfigs: MutableList<StreamConfig> = ArrayList()
        for (stream in catalog.streams) {
            val originalStreamConfig = toStreamConfig(stream)
            val actualStreamConfig: StreamConfig
            // Use empty string quote because we don't really care
            if (
                streamConfigs.stream().anyMatch { s: StreamConfig ->
                    s.id.finalTableId("") == originalStreamConfig.id.finalTableId("")
                } ||
                    streamConfigs.stream().anyMatch { s: StreamConfig ->
                        s.id.rawTableId("") == originalStreamConfig.id.rawTableId("")
                    }
            ) {
                val originalNamespace = stream.stream.namespace
                val originalName = stream.stream.name

                LOGGER.info(
                    "Detected table name collision for {}.{}",
                    originalNamespace,
                    originalName
                )

                // ... this logic is ported from legacy normalization, and maybe should change?
                // We're taking a hash of the quoted namespace and the unquoted stream name
                val hash =
                    DigestUtils.sha1Hex(
                            "${originalStreamConfig.id.finalNamespace}&airbyte&$originalName"
                        )
                        .substring(0, 3)
                val newName = "${originalName}_$hash"
                actualStreamConfig =
                    StreamConfig(
                        sqlGenerator.buildStreamId(originalNamespace, newName, rawNamespace),
                        originalStreamConfig.syncMode,
                        originalStreamConfig.destinationSyncMode,
                        originalStreamConfig.primaryKey,
                        originalStreamConfig.cursor,
                        originalStreamConfig.columns,
                    )
            } else {
                actualStreamConfig = originalStreamConfig
            }
            streamConfigs.add(
                actualStreamConfig.copy(
                    // If we had collisions, we modified the stream name.
                    // Revert those changes.
                    id =
                        actualStreamConfig.id.copy(
                            originalName = stream.stream.name,
                            originalNamespace = stream.stream.namespace,
                        ),
                ),
            )

            // Populate some interesting strings into the exception handler string deinterpolator
            addStringForDeinterpolation(actualStreamConfig.id.rawNamespace)
            addStringForDeinterpolation(actualStreamConfig.id.rawName)
            addStringForDeinterpolation(actualStreamConfig.id.finalNamespace)
            addStringForDeinterpolation(actualStreamConfig.id.finalName)
            addStringForDeinterpolation(actualStreamConfig.id.originalNamespace)
            addStringForDeinterpolation(actualStreamConfig.id.originalName)
            actualStreamConfig.columns.keys.forEach(
                Consumer { columnId: ColumnId? ->
                    addStringForDeinterpolation(columnId!!.name)
                    addStringForDeinterpolation(columnId.originalName)
                }
            )
            // It's (unfortunately) possible for a cursor/PK to be declared that don't actually
            // exist in the
            // schema.
            // Add their strings explicitly.
            actualStreamConfig.cursor.ifPresent { cursor: ColumnId ->
                addStringForDeinterpolation(cursor.name)
                addStringForDeinterpolation(cursor.originalName)
            }
            actualStreamConfig.primaryKey.forEach(
                Consumer { pk: ColumnId ->
                    addStringForDeinterpolation(pk.name)
                    addStringForDeinterpolation(pk.originalName)
                }
            )
        }
        LOGGER.info("Running sync with stream configs: $streamConfigs")
        return ParsedCatalog(streamConfigs)
    }

    @VisibleForTesting
    fun toStreamConfig(stream: ConfiguredAirbyteStream): StreamConfig {
        val airbyteColumns =
            when (
                val schema: AirbyteType =
                    AirbyteType.Companion.fromJsonSchema(stream.stream.jsonSchema)
            ) {
                is Struct -> schema.properties
                is Union -> schema.asColumns()
                else -> throw IllegalArgumentException("Top-level schema must be an object")
            }

        require(!stream.primaryKey.stream().anyMatch { key: List<String?> -> key.size > 1 }) {
            "Only top-level primary keys are supported"
        }
        val primaryKey =
            stream.primaryKey
                .stream()
                .map { key: List<String> -> sqlGenerator.buildColumnId(key[0]) }
                .toList()

        require(stream.cursorField.size <= 1) { "Only top-level cursors are supported" }
        val cursor: Optional<ColumnId> =
            if (stream.cursorField.isNotEmpty()) {
                Optional.of(sqlGenerator.buildColumnId(stream.cursorField[0]))
            } else {
                Optional.empty()
            }

        val columns = resolveColumnCollisions(airbyteColumns, stream)

        return StreamConfig(
            sqlGenerator.buildStreamId(stream.stream.namespace, stream.stream.name, rawNamespace),
            stream.syncMode,
            stream.destinationSyncMode,
            primaryKey,
            cursor,
            columns
        )
    }

    /**
     * This code is really bad and I'm not convinced we need to preserve this behavior. As with the
     * tablename collisions thing above - we're trying to preserve legacy normalization's naming
     * conventions here.
     */
    private fun resolveColumnCollisions(
        airbyteColumns: LinkedHashMap<String, AirbyteType>,
        stream: ConfiguredAirbyteStream
    ): LinkedHashMap<ColumnId, AirbyteType> {
        val columns = LinkedHashMap<ColumnId, AirbyteType>()
        for ((key, value) in airbyteColumns) {
            val originalColumnId = sqlGenerator.buildColumnId(key)
            var columnId: ColumnId
            if (
                columns.keys.stream().noneMatch { c: ColumnId ->
                    c.canonicalName == originalColumnId.canonicalName
                }
            ) {
                // None of the existing columns have the same name. We can add this new column
                // as-is.
                columnId = originalColumnId
            } else {
                LOGGER.info(
                    "Detected column name collision for {}.{}.{}",
                    stream.stream.namespace,
                    stream.stream.name,
                    key,
                )
                // One of the existing columns has the same name. We need to handle this collision.
                // Append _1, _2, _3, ... to the column name until we find one that doesn't collide.
                var i = 1
                while (true) {
                    columnId = sqlGenerator.buildColumnId(key, "_$i")

                    // Verify that we're making progress, e.g. we haven't immediately truncated away
                    // the suffix.
                    if (columnId.canonicalName == originalColumnId.canonicalName) {
                        // If we're not making progress, do a more powerful mutation instead of
                        // appending numbers.
                        // Assume that we're being truncated, and that the column ID's name is the
                        // maximum length.
                        columnId =
                            superResolveColumnCollisions(
                                originalColumnId,
                                columns,
                                originalColumnId.name.length
                            )
                        break
                    }

                    val canonicalName = columnId.canonicalName
                    if (
                        columns.keys.stream().noneMatch { c: ColumnId ->
                            c.canonicalName == canonicalName
                        }
                    ) {
                        break
                    } else {
                        i++
                    }
                }
                // But we need to keep the original name so that we can still fetch it out of the
                // JSON records.
                columnId =
                    ColumnId(
                        columnId.name,
                        originalColumnId.originalName,
                        columnId.canonicalName,
                    )
            }

            columns[columnId] = value
        }
        return columns
    }

    /**
     * Generate a name of the format `<prefix><length><suffix>`. E.g. for affixLength=3:
     * "veryLongName" -> "ver6ame" This is based on the "i18n"-ish naming convention.
     *
     * @param columnId The column that we're trying to add
     * @param columns The columns that we've already added
     */
    private fun superResolveColumnCollisions(
        columnId: ColumnId,
        columns: LinkedHashMap<ColumnId, AirbyteType>,
        maximumColumnNameLength: Int
    ): ColumnId {
        val originalColumnName = columnId.originalName

        var newColumnId = columnId
        // Assume that the <length> portion can be expressed in at most 5 characters.
        // If someone is giving us a column name that's longer than 99999 characters,
        // that's just being silly.
        val affixLength = (maximumColumnNameLength - 5) / 2
        // If, after reserving 5 characters for the length, we can't fit the affixes,
        // just give up. That means the destination is trying to restrict us to a
        // 6-character column name, which is just silly.
        if (affixLength <= 0) {
            throw IllegalArgumentException(
                "Cannot solve column name collision: ${newColumnId.originalName}. We recommend removing this column to continue syncing."
            )
        }
        val prefix = originalColumnName.substring(0, affixLength)
        val suffix =
            originalColumnName.substring(
                originalColumnName.length - affixLength,
                originalColumnName.length
            )
        val length = originalColumnName.length - 2 * affixLength
        newColumnId = sqlGenerator.buildColumnId("$prefix$length$suffix")
        // if there's _still_ a collision after this, just give up.
        // we could try to be more clever, but this is already a pretty rare case.
        if (
            columns.keys.stream().anyMatch { c: ColumnId ->
                c.canonicalName == newColumnId.canonicalName
            }
        ) {
            throw IllegalArgumentException(
                "Cannot solve column name collision: ${newColumnId.originalName}. We recommend removing this column to continue syncing."
            )
        }
        return newColumnId
    }

    companion object {
        private val LOGGER: Logger = LoggerFactory.getLogger(CatalogParser::class.java)
    }
}
