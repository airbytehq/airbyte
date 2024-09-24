/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.mysql.cdc

import io.airbyte.cdk.jdbc.JdbcConnectionFactory
import io.airbyte.cdk.read.CdcPositionMapper
import io.airbyte.cdk.read.DebeziumRecord
import io.github.oshai.kotlinlogging.KotlinLogging
import io.micronaut.context.annotation.Primary
import jakarta.inject.Singleton
import java.sql.Connection
import java.sql.ResultSet
import org.apache.kafka.connect.source.SourceRecord

class MySqlCdcPositionMapper(jdbcConnectionFactory: JdbcConnectionFactory) : CdcPositionMapper {

    val conn: Connection = jdbcConnectionFactory.get()
    private val log = KotlinLogging.logger {}
    val targetPosition: MySqlTargetPosition
    init {
        val rs: ResultSet = conn.createStatement().executeQuery("SHOW MASTER STATUS")
        rs.next()
        targetPosition = MySqlTargetPosition(rs.getString("File"), rs.getLong("Position"))
    }
    override fun reachedTargetPosition(record: DebeziumRecord): Boolean {
        val eventFileName: String = record.source().get("file").asText()
        val eventPosition: Long = record.source().get("pos").asLong()
        return reachedTargetPosition(eventFileName, eventPosition)
    }

    override fun reachedTargetPosition(record: SourceRecord): Boolean {
        val eventFileName: String = record.sourceOffset()["file"].toString()
        val eventPosition: Long = record.sourceOffset()["pos"] as Long
        return reachedTargetPosition(eventFileName, eventPosition)
    }

    internal fun reachedTargetPosition(eventFileName: String, eventPosition: Long): Boolean {
        val isEventPositionAfter =
            eventFileName.compareTo(targetPosition.fileName) > 0 ||
                (eventFileName.compareTo(
                    targetPosition.fileName,
                ) == 0 && eventPosition >= targetPosition.position)
        if (isEventPositionAfter) {
            log.info {
                "Signalling close because record's binlog file : " +
                    eventFileName +
                    " , position : " +
                    eventPosition +
                    " is after target file : " +
                    targetPosition.fileName +
                    " , target position : " +
                    targetPosition.position
            }
        }
        return isEventPositionAfter
    }
}

@Singleton
@Primary
class MySqlCdcPositionMapperFactory(jdbcConnectionFactory: JdbcConnectionFactory) :
    CdcPositionMapper.Factory {

    val jdbcConnectionFactory = jdbcConnectionFactory
    override fun get(): CdcPositionMapper {
        return MySqlCdcPositionMapper(jdbcConnectionFactory)
    }
}

data class MySqlTargetPosition(val fileName: String, val position: Long)
