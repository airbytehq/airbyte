/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.file.csv

import io.airbyte.cdk.load.data.ObjectType
import io.airbyte.cdk.load.data.csv.toCsvHeader
import java.io.OutputStream
import java.io.PrintWriter
import java.nio.charset.StandardCharsets
import org.apache.commons.csv.CSVFormat
import org.apache.commons.csv.CSVPrinter
import org.apache.commons.csv.QuoteMode

@Suppress("DEPRECATION")
fun ObjectType.toCsvPrinterWithHeader(
    outputStream: OutputStream,
    csvSettings: CSVFormat = CSVFormat.DEFAULT.withQuoteMode(QuoteMode.NON_NUMERIC)
): CSVPrinter {
    return CSVPrinter(
        PrintWriter(outputStream, true, StandardCharsets.UTF_8),
        csvSettings.withHeader(*toCsvHeader())
    )
}
