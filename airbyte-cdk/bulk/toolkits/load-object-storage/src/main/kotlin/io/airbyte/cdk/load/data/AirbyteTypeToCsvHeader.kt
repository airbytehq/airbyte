/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import java.io.Writer
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter

class AirbyteTypeToCsvHeader {
    fun convert(schema: ObjectType): Array<String> {
        return schema.properties.map { it.key }.toTypedArray()
    }
}

fun ObjectType.toCsvHeader(): Array<String> {
    return AirbyteTypeToCsvHeader().convert(this)
}

fun ObjectType.toCsvPrinterWithHeader(writer: Writer): CSVPrinter =
    CSVFormat.Builder.create().setHeader(*toCsvHeader()).setAutoFlush(true).build().print(writer)
