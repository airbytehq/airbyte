/*
 * Copyright (c) 2024 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.cdk.integrations.destination.async

import java.text.DecimalFormat

/**
 * Replicate the behavior of [org.apache.commons.io.FileUtils] to match the proclivities of Davin
 * and Charles. Courteously written by ChatGPT.
 */
object AirbyteFileUtils {
    private const val ONE_KB = 1024.0
    private const val ONE_MB = ONE_KB * 1024
    private const val ONE_GB = ONE_MB * 1024
    private const val ONE_TB = ONE_GB * 1024
    private val df = DecimalFormat("#.##")

    /**
     * Replicate the behavior of [org.apache.commons.io.FileUtils] but instead of rounding down to
     * the nearest whole number, it rounds to two decimal places.
     *
     * @param sizeInBytes size in bytes
     * @return human-readable size
     */
    fun byteCountToDisplaySize(sizeInBytes: Long): String {
        return if (sizeInBytes < ONE_KB) {
            df.format(sizeInBytes) + " bytes"
        } else if (sizeInBytes < ONE_MB) {
            df.format(sizeInBytes.toDouble() / ONE_KB) + " KB"
        } else if (sizeInBytes < ONE_GB) {
            df.format(sizeInBytes.toDouble() / ONE_MB) + " MB"
        } else if (sizeInBytes < ONE_TB) {
            df.format(sizeInBytes.toDouble() / ONE_GB) + " GB"
        } else {
            df.format(sizeInBytes.toDouble() / ONE_TB) + " TB"
        }
    }
}
