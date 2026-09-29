/*
 * Copyright (c) 2025 Airbyte, Inc., all rights reserved.
 */

package io.airbyte.integrations.source.postgres.ctid

import java.util.regex.Pattern

data class Ctid(val page: Long, val tuple: Long) {
    override fun toString(): String = "($page,$tuple)"

    companion object {
        val ZERO: Ctid = Ctid(0, 0)

        fun of(ctid: String): Ctid {
            val p = Pattern.compile("\\d+")
            val m = p.matcher(ctid)
            require(m.find()) { "Invalid ctid format" }
            val ctidPageStr = m.group()
            val page: Long = ctidPageStr.toLong()

            require(m.find()) { "Invalid ctid format" }
            val ctidTupleStr = m.group()
            val tuple: Long = ctidTupleStr.toLong()

            return Ctid(page, tuple)
        }

        fun inc(ctid: Ctid, maxTuple: Long): Ctid =
            if (ctid.tuple + 1 > maxTuple) Ctid(ctid.page + 1, 1)
            else Ctid(ctid.page, ctid.tuple + 1)
    }
}
