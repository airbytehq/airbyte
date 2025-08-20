package io.airbyte.integrations.source.postgres.ctid

import java.util.*
import java.util.regex.Pattern

class Ctid {
    val page: Long
    val tuple: Long

    internal constructor(page: Long, tuple: Long) {
        this.page = page
        this.tuple = tuple
    }

    internal constructor(ctid: String) {
        val p = Pattern.compile("\\d+")
        val m = p.matcher(ctid)
        require(m.find()) { "Invalid ctid format" }
        val ctidPageStr = m.group()
        this.page = ctidPageStr.toLong()

        require(m.find()) { "Invalid ctid format" }
        val ctidTupleStr = m.group()
        this.tuple = ctidTupleStr.toLong()

        Objects.requireNonNull<Long?>(this.page)
        Objects.requireNonNull<Long?>(this.tuple)
    }

    override fun toString(): String = "($page,$tuple)"


    override fun equals(o: Any?): Boolean {
        if (this === o) {
            return true
        }
        if (o == null || javaClass != o.javaClass) {
            return false
        }
        val ctid = o as Ctid
        return page == ctid.page && tuple == ctid.tuple
    }

    override fun hashCode(): Int {
        return Objects.hash(page, tuple)
    }

    companion object {
        val ZERO: Ctid = of(0, 0)

        fun of(page: Long, tuple: Long): Ctid {
            return Ctid(page, tuple)
        }

        fun of(ctid: String): Ctid {
            return Ctid(ctid)
        }

        fun inc(ctid: Ctid, maxTuple: Long): Ctid {
            return if (ctid.tuple + 1 > maxTuple) of(ctid.page + 1, 1) else of(
                ctid.page,
                ctid.tuple + 1,
            )
        }
    }
}
