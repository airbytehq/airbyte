/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.integrations.destination.jdbc.constants

import io.aesy.datasize.ByteUnit
import io.aesy.datasize.DataSize

interface GlobalDataSizeConstants {
    companion object {
        /** 25 MB to BYTES as comparison will be done in BYTES */
        @JvmField
        val DEFAULT_MAX_BATCH_SIZE_BYTES: Int =
            DataSize.of(25L, ByteUnit.IEC.MEBIBYTE).toUnit(ByteUnit.IEC.BYTE).value.toInt()

        /**
         * This constant determines the max possible size of file(e.g. 100 MB / 25 megabytes ≈ 4
         * chunks of file) see StagingFilenameGenerator.java:28
         */
        @JvmField
        val MAX_FILE_SIZE: Long =
            DataSize.of(100L, ByteUnit.IEC.MEBIBYTE).toUnit(ByteUnit.IEC.BYTE).value.toLong()
    }
}
