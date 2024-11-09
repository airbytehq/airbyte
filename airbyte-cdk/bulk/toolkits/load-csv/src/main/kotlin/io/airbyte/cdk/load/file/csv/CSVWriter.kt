/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.csv

import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.csv.toCsvHeader
import java.io.OutputStream
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter

fun ObjectType.toCsvPrinterWithHeader(outputStream: OutputStream): CSVPrinter =
    CSVFormat.Builder.create()
        .setHeader(*toCsvHeader())
        .setAutoFlush(true)
        .build()
        .print(outputStream.writer(charset = Charsets.UTF_8))
