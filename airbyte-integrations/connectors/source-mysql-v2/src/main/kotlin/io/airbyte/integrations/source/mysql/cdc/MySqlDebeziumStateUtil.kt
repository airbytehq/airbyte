/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import io.github.oshai.kotlinlogging.KotlinLogging
import java.sql.Connection
import java.sql.ResultSet
import java.sql.SQLException
import java.time.Instant
import java.util.*

class MySqlDebeziumStateUtil {
    companion object {
        private val log = KotlinLogging.logger {}

        /**
         * Method to construct initial Debezium state which can be passed onto Debezium engine to
         * make it process binlogs from a specific file and position and skip snapshot phase
         */
        fun constructBinlogOffset(
            conn: Connection,
            debeziumName: String,
            topicPrefixName: String
        ): JsonNode {
            return format(
                getStateAttributesFromDB(conn),
                debeziumName,
                topicPrefixName,
                Instant.now(),
            )
        }

        fun format(
            attributes: MysqlDebeziumStateAttributes,
            debeziumName: String,
            topicPrefixName: String,
            time: Instant
        ): JsonNode {
            val key = "[\"$debeziumName\",{\"server\":\"$topicPrefixName\"}]"
            val gtidSet =
                if (attributes.gtidSet.isPresent())
                    ",\"gtids\":\"" + attributes.gtidSet.get() + "\""
                else ""
            val value =
                ("{\"transaction_id\":null,\"ts_sec\":" +
                    time.epochSecond +
                    ",\"file\":\"" +
                    attributes.binlogFilename +
                    "\",\"pos\":" +
                    attributes.binlogPosition +
                    gtidSet +
                    "}")

            val result: MutableMap<String, String> = HashMap()
            result[key] = value
            val jsonNode: JsonNode = ObjectMapper().valueToTree(result)
            log.info { "Constructed binlog offset: $jsonNode" }
            return jsonNode
        }

        fun getStateAttributesFromDB(conn: Connection): MysqlDebeziumStateAttributes {
            try {
                val resultSet: ResultSet = conn.createStatement().executeQuery("SHOW MASTER STATUS")
                resultSet.next()
                val file = resultSet.getString("File")
                val position = resultSet.getLong("Position")
                assert(file != null)
                assert(position >= 0)
                if (resultSet.metaData.columnCount > 4) {
                    // This column exists only in MySQL 5.6.5 or later ...
                    val gtidSet =
                        resultSet.getString(
                            5
                        ) // GTID set, may be null, blank, or contain a GTID set
                    return MysqlDebeziumStateAttributes(
                        file,
                        position,
                        removeNewLineChars(
                            gtidSet,
                        ),
                    )
                } else {
                    return MysqlDebeziumStateAttributes(
                        file,
                        position,
                        Optional.empty<String>(),
                    )
                }
            } catch (e: SQLException) {
                throw RuntimeException(e)
            }
        }

        private fun removeNewLineChars(gtidSet: String?): Optional<String> {
            if (gtidSet != null && !gtidSet.trim { it <= ' ' }.isEmpty()) {
                // Remove all the newline chars that exist in the GTID set string ...
                return Optional.of(gtidSet.replace("\n", "").replace("\r", ""))
            }

            return Optional.empty()
        }

        data class MysqlDebeziumStateAttributes(
            val binlogFilename: String,
            val binlogPosition: Long,
            val gtidSet: Optional<String>
        )
    }
}
