/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.s3.csv

import com.fasterxml.jackson.databind.JsonNode
import io.airbyte.protocol.models.v0.AirbyteRecordMessage
import java.util.*

/**
 * CSV data row = ID column + timestamp column + record columns. This class takes care of the first
 * two columns, which is shared by downstream implementations.
 */
abstract class BaseSheetGenerator : CsvSheetGenerator {
    override fun getDataRow(id: UUID, recordMessage: AirbyteRecordMessage): List<Any> {
        val data: MutableList<Any> = LinkedList()
        data.add(id)
        data.add(recordMessage.emittedAt)
        data.addAll(getRecordColumns(recordMessage.data)!!)
        return data
    }

    override fun getDataRow(formattedData: JsonNode): List<Any> {
        return LinkedList<Any>(getRecordColumns(formattedData))
    }

    override fun getDataRow(
        id: UUID,
        formattedString: String,
        emittedAt: Long,
        formattedAirbyteMetaString: String
    ): List<Any> {
        // TODO: Make this abstract or default if No-op is intended in NoFlatteningSheetGenerator or
        // RootLevelFlatteningSheetGenerator
        throw UnsupportedOperationException("Not implemented in BaseSheetGenerator")
    }

    abstract fun getRecordColumns(json: JsonNode): List<String>?
}
