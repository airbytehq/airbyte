/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data.csv

import io.airbyte.cdk.load.data.AirbyteType
import io.airbyte.cdk.load.data.AirbyteValue
import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.ObjectValue
import io.airbyte.cdk.load.data.StringValue
import io.airbyte.cdk.load.data.json.toAirbyteValue
import io.airbyte.cdk.load.message.Meta
import io.airbyte.cdk.load.util.deserializeToNode
import org.apache.commons.csv.CSVRecord

class CsvRowToAirbyteValue {
    fun convert(row: CSVRecord, schema: AirbyteType): AirbyteValue {
        if (schema !is ObjectType) {
            throw IllegalArgumentException("Only object types are supported")
        }

        return ObjectValue(
            row.parser.headerNames.zip(row.toList()).associateTo(linkedMapOf()) { (key, valueString)
                ->
                val airbyteValue =
                    if (Meta.COLUMN_NAMES.contains(key)) {
                        Meta.getMetaValue(key, valueString)
                    } else {
                        try {
                            valueString.deserializeToNode().toAirbyteValue()
                        } catch (e: Exception) {
                            // boolean/number/object/array can deserialize cleanly
                            // but strings don't work, so just handle them here
                            StringValue(valueString)
                        }
                    }
                key to airbyteValue
            },
        )
    }
}

fun CSVRecord.toAirbyteValue(schema: AirbyteType): AirbyteValue {
    return CsvRowToAirbyteValue().convert(this, schema)
}
