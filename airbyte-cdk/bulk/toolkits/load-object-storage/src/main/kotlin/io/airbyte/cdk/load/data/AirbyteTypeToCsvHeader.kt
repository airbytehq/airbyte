/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import java.io.Writer
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter

class AirbyteTypeToCsvHeader {
    fun convert(schema: AirbyteType): Array<String> {
        if (schema !is ObjectType) {
            throw IllegalArgumentException("Only object types are supported")
        }
        return schema.properties.map { it.key }.toTypedArray()
    }
}

fun AirbyteType.toCsvHeader(): Array<String> {
    return AirbyteTypeToCsvHeader().convert(this)
}

fun AirbyteType.toCsvPrinterWithHeader(writer: Writer): CSVPrinter =
    CSVFormat.Builder.create().setHeader(*toCsvHeader()).build().print(writer)
