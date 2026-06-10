/*
 * Copyright (c) 2026 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.load.data

import java.time.format.DateTimeFormatter

/**
 * Lenient DateTimeFormatter patterns used across the CDK for parsing temporal strings from sources.
 * These support a wide range of formats (ISO-8601, slashes, dots, abbreviated months, eras, etc.)
 * to handle the variety of timestamp representations emitted by different source connectors.
 */
object TemporalFormatters {
    val DATE_TIME_FORMATTER: DateTimeFormatter =
        DateTimeFormatter.ofPattern(
            "[yyyy][yy]['-']['/']['.'][' '][MMM][MM][M]['-']['/']['.'][' '][dd][d][[' '][G]][[' ']['T']HH:mm[':'ss[.][SSSSSS][SSSSS][SSSS][SSS][' '][z][zzz][Z][O][x][XXX][XX][X][[' '][G]]]]"
        )
    val TIME_FORMATTER: DateTimeFormatter =
        DateTimeFormatter.ofPattern(
            "HH:mm[':'ss[.][SSSSSS][SSSSS][SSSS][SSS][' '][z][zzz][Z][O][x][XXX][XX][X]]"
        )
}
