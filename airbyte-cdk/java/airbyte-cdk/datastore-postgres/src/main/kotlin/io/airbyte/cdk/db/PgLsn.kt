/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.cdk.db

import com.google.common.annotations.VisibleForTesting
import com.google.common.base.Preconditions
import java.nio.ByteBuffer
import java.util.*

/**
 * Doc on the structure of a Postgres LSN
 * https://www.postgresql.org/docs/current/datatype-pg-lsn.html
 */
class PgLsn private constructor(private val lsn: Long) : Comparable<PgLsn> {
    fun asLong(): Long {
        return lsn
    }

    fun asPgString(): String {
        return longToLsn(lsn)
    }

    override fun compareTo(other: PgLsn): Int {
        return java.lang.Long.compare(lsn, other.asLong())
    }

    override fun toString(): String {
        return "PgLsn{" + "lsn=" + lsn + '}'
    }

    companion object {
        @JvmStatic
        fun fromLong(lsn: Long): PgLsn {
            return PgLsn(lsn)
        }

        @JvmStatic
        fun fromPgString(lsn: String): PgLsn {
            return PgLsn(lsnToLong(lsn))
        }

        /**
         * The LSN returned by Postgres is a 64-bit integer represented as hex encoded 32-bit
         * integers separated by a /. reference: https://github.com/davecramer/LogicalDecode
         *
         * @param lsn string representation as returned by postgres
         * @return long representation of the lsn string.
         */
        @JvmStatic
        @VisibleForTesting
        fun lsnToLong(lsn: String): Long {
            val slashIndex = lsn.lastIndexOf('/')
            Preconditions.checkArgument(slashIndex >= 0)

            val logicalXLogStr = lsn.substring(0, slashIndex)
            // parses as a long but then cast to int. this allows us to retain the full 32 bits of
            // the integer
            // as opposed to the reduced value of Integer.MAX_VALUE.
            val logicalXlog = logicalXLogStr.toLong(16).toInt()
            val segmentStr = lsn.substring(slashIndex + 1, lsn.length)
            val segment = segmentStr.toLong(16).toInt()

            val buf = ByteBuffer.allocate(8)
            buf.putInt(logicalXlog)
            buf.putInt(segment)
            buf.position(0)
            return buf.getLong()
        }

        @JvmStatic
        @VisibleForTesting
        fun longToLsn(long1: Long): String {
            val front = (long1 shr 32).toInt()
            val back = long1.toInt()
            return (Integer.toHexString(front) + "/" + Integer.toHexString(back)).uppercase(
                Locale.getDefault()
            )
        }
    }
}
