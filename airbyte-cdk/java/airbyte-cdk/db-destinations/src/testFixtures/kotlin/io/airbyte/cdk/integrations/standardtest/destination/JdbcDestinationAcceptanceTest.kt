/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.standardtest.destination

import com.fasterxml.jackson.databind.JsonNode
import com.fasterxml.jackson.databind.ObjectMapper
import java.util.*
import java.util.function.Function
import org.jooq.Field
import org.jooq.Record

abstract class JdbcDestinationAcceptanceTest : DestinationAcceptanceTest() {
    protected val mapper: ObjectMapper = ObjectMapper()

    protected fun getJsonFromRecord(record: Record): JsonNode {
        return getJsonFromRecord(record, Function { x: Any? -> Optional.empty() })
    }

    protected fun getJsonFromRecord(
        record: Record,
        valueParser: Function<Any, Optional<String>>
    ): JsonNode {
        val node = mapper.createObjectNode()

        Arrays.stream(record.fields()).forEach { field: Field<*> ->
            val value = record[field]
            val parsedValue = valueParser.apply(value)
            if (parsedValue.isPresent) {
                node.put(field.name, parsedValue.get())
            } else {
                when (field.dataType.typeName) {
                    "varchar",
                    "nvarchar",
                    "jsonb",
                    "json",
                    "other" -> {
                        val stringValue = (value?.toString())
                        DestinationAcceptanceTestUtils.putStringIntoJson(
                            stringValue,
                            field.name,
                            node
                        )
                    }
                    else -> node.put(field.name, (value?.toString()))
                }
            }
        }
        return node
    }
}
