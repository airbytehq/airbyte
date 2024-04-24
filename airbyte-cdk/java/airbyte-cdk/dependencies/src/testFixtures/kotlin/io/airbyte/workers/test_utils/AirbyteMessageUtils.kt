/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.workers.test_utils

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.ImmutableMap
import io.airbyte.commons.json.Jsons
import io.airbyte.protocol.models.*
import java.time.Instant

object AirbyteMessageUtils {
    fun createRecordMessage(
        tableName: String?,
        record: JsonNode?,
        timeExtracted: Instant
    ): AirbyteMessage {
        return AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(
                AirbyteRecordMessage()
                    .withData(record)
                    .withStream(tableName)
                    .withEmittedAt(timeExtracted.epochSecond)
            )
    }

    fun createLogMessage(level: AirbyteLogMessage.Level?, message: String?): AirbyteMessage {
        return AirbyteMessage()
            .withType(AirbyteMessage.Type.LOG)
            .withLog(AirbyteLogMessage().withLevel(level).withMessage(message))
    }

    fun createRecordMessage(tableName: String?, key: String, value: String): AirbyteMessage {
        return createRecordMessage(tableName, ImmutableMap.of(key, value))
    }

    fun createRecordMessage(tableName: String?, key: String, value: Int): AirbyteMessage {
        return createRecordMessage(tableName, ImmutableMap.of(key, value))
    }

    fun createRecordMessage(tableName: String?, record: Map<String, *>?): AirbyteMessage {
        return createRecordMessage(tableName, Jsons.jsonNode(record), Instant.EPOCH)
    }

    fun createRecordMessage(streamName: String?, recordData: Int): AirbyteMessage {
        return AirbyteMessage()
            .withType(AirbyteMessage.Type.RECORD)
            .withRecord(
                AirbyteRecordMessage().withStream(streamName).withData(Jsons.jsonNode(recordData))
            )
    }

    fun createStateMessage(stateData: Int): AirbyteMessage {
        return AirbyteMessage()
            .withType(AirbyteMessage.Type.STATE)
            .withState(AirbyteStateMessage().withData(Jsons.jsonNode(stateData)))
    }

    fun createStateMessage(key: String, value: String): AirbyteMessage {
        return AirbyteMessage()
            .withType(AirbyteMessage.Type.STATE)
            .withState(AirbyteStateMessage().withData(Jsons.jsonNode(ImmutableMap.of(key, value))))
    }

    fun createStreamStateMessage(streamName: String?, stateData: Int): AirbyteStateMessage {
        return AirbyteStateMessage()
            .withType(AirbyteStateMessage.AirbyteStateType.STREAM)
            .withStream(createStreamState(streamName).withStreamState(Jsons.jsonNode(stateData)))
    }

    fun createGlobalStateMessage(stateData: Int, vararg streamNames: String?): AirbyteMessage {
        val streamStates: MutableList<AirbyteStreamState> = ArrayList()
        for (streamName in streamNames) {
            streamStates.add(
                createStreamState(streamName).withStreamState(Jsons.jsonNode(stateData))
            )
        }
        return AirbyteMessage()
            .withType(AirbyteMessage.Type.STATE)
            .withState(
                AirbyteStateMessage()
                    .withType(AirbyteStateMessage.AirbyteStateType.GLOBAL)
                    .withGlobal(AirbyteGlobalState().withStreamStates(streamStates))
            )
    }

    fun createStreamState(streamName: String?): AirbyteStreamState {
        return AirbyteStreamState().withStreamDescriptor(StreamDescriptor().withName(streamName))
    }

    fun createStreamEstimateMessage(
        name: String?,
        namespace: String?,
        byteEst: Long,
        rowEst: Long
    ): AirbyteMessage {
        return createEstimateMessage(
            AirbyteEstimateTraceMessage.Type.STREAM,
            name,
            namespace,
            byteEst,
            rowEst
        )
    }

    fun createSyncEstimateMessage(byteEst: Long, rowEst: Long): AirbyteMessage {
        return createEstimateMessage(
            AirbyteEstimateTraceMessage.Type.SYNC,
            null,
            null,
            byteEst,
            rowEst
        )
    }

    fun createEstimateMessage(
        type: AirbyteEstimateTraceMessage.Type?,
        name: String?,
        namespace: String?,
        byteEst: Long,
        rowEst: Long
    ): AirbyteMessage {
        val est =
            AirbyteEstimateTraceMessage()
                .withType(type)
                .withByteEstimate(byteEst)
                .withRowEstimate(rowEst)

        if (name != null) {
            est.withName(name)
        }
        if (namespace != null) {
            est.withNamespace(namespace)
        }

        return AirbyteMessage()
            .withType(AirbyteMessage.Type.TRACE)
            .withTrace(
                AirbyteTraceMessage().withType(AirbyteTraceMessage.Type.ESTIMATE).withEstimate(est)
            )
    }

    fun createErrorMessage(message: String?, emittedAt: Double?): AirbyteMessage {
        return AirbyteMessage()
            .withType(AirbyteMessage.Type.TRACE)
            .withTrace(createErrorTraceMessage(message, emittedAt))
    }

    @JvmOverloads
    fun createErrorTraceMessage(
        message: String?,
        emittedAt: Double?,
        failureType: AirbyteErrorTraceMessage.FailureType? = null
    ): AirbyteTraceMessage {
        val msg =
            AirbyteTraceMessage()
                .withType(AirbyteTraceMessage.Type.ERROR)
                .withError(AirbyteErrorTraceMessage().withMessage(message))
                .withEmittedAt(emittedAt)

        if (failureType != null) {
            msg.error.withFailureType(failureType)
        }

        return msg
    }

    fun createConfigControlMessage(config: Config?, emittedAt: Double?): AirbyteMessage {
        return AirbyteMessage()
            .withType(AirbyteMessage.Type.CONTROL)
            .withControl(
                AirbyteControlMessage()
                    .withEmittedAt(emittedAt)
                    .withType(AirbyteControlMessage.Type.CONNECTOR_CONFIG)
                    .withConnectorConfig(AirbyteControlConnectorConfigMessage().withConfig(config))
            )
    }
}
