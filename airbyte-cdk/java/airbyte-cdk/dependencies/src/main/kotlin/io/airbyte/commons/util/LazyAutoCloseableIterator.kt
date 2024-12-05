/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.util

import com.google.common.base.Preconditions
import com.google.common.collect.AbstractIterator
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import java.util.*
import java.util.function.Supplier

/**
 * A [AutoCloseableIterator] that calls the provided supplier the first time
 * [AutoCloseableIterator.hasNext] or [AutoCloseableIterator.next] is called. If
 * [AutoCloseableIterator.hasNext] or [AutoCloseableIterator.next] are never called, then the
 * supplier will never be called. This means if the iterator is closed in this state, the close
 * function on the input iterator will not be called. The assumption here is that if nothing is ever
 * supplied, then there is nothing to close.
 *
 * @param <T> type </T>
 */
internal class LazyAutoCloseableIterator<T>(
    iteratorSupplier: Supplier<AutoCloseableIterator<T>>,
    airbyteStream: AirbyteStreamNameNamespacePair?
) : AbstractIterator<T>(), AutoCloseableIterator<T> {
    private val iteratorSupplier: Supplier<AutoCloseableIterator<T>>
    override val airbyteStream: Optional<AirbyteStreamNameNamespacePair>
    private var hasSupplied: Boolean
    private var internalIterator: AutoCloseableIterator<T>? = null

    init {
        Preconditions.checkNotNull(iteratorSupplier)
        this.airbyteStream = Optional.ofNullable(airbyteStream)
        this.iteratorSupplier = iteratorSupplier
        this.hasSupplied = false
    }

    override fun computeNext(): T? {
        if (!hasSupplied) {
            internalIterator = iteratorSupplier.get()
            Preconditions.checkNotNull(internalIterator, "Supplied iterator was null.")
            hasSupplied = true
        }

        return if (internalIterator!!.hasNext()) {
            internalIterator!!.next()
        } else {
            endOfData()
        }
    }

    @Throws(Exception::class)
    override fun close() {
        if (internalIterator != null) {
            internalIterator!!.close()
        }
    }
}
