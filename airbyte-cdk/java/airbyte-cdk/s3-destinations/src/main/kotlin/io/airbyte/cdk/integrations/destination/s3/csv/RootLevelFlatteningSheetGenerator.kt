/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.s3.csv

import com.fasterxml.jackson.databind.JsonNode
import com.google.common.collect.Lists
import io.airbyte.cdk.integrations.base.JavaBaseConstants
import io.airbyte.commons.json.Jsons
import io.airbyte.commons.util.MoreIterators
import java.util.LinkedList

class RootLevelFlatteningSheetGenerator(jsonSchema: JsonNode) :
    BaseSheetGenerator(), CsvSheetGenerator {
    /** Keep a header list to iterate the input json object with a defined order. */
    private val recordHeaders: List<String> =
        MoreIterators.toList(
                jsonSchema["properties"].fieldNames(),
            )
            .sorted()

    override fun getHeaderRow(): List<String> {
        val headers: MutableList<String> =
            Lists.newArrayList(
                JavaBaseConstants.COLUMN_NAME_AB_ID,
                JavaBaseConstants.COLUMN_NAME_EMITTED_AT,
            )
        headers.addAll(recordHeaders)
        return headers
    }

    /** With root level flattening, the record columns are the first level fields of the json. */
    override fun getRecordColumns(json: JsonNode): List<String> {
        val values: MutableList<String> = LinkedList()
        for (field in recordHeaders) {
            val value = json[field]
            if (value == null) {
                values.add("")
            } else if (value.isValueNode) {
                // Call asText method on value nodes so that proper string
                // representation of json values can be returned by Jackson.
                // Otherwise, CSV printer will just call the toString method,
                // which can be problematic (e.g. text node will have extra
                // double quotation marks around its text value).
                values.add(value.asText())
            } else {
                values.add(Jsons.serialize(value))
            }
        }

        return values
    }
}
