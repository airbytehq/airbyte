/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.util

import com.google.common.base.Preconditions
import com.google.common.collect.AbstractIterator
import io.airbyte.commons.concurrency.VoidCallable
import io.airbyte.protocol.models.AirbyteStreamNameNamespacePair
import java.util.*

/**
 * The canonical [AutoCloseableIterator]. The default behavior guarantees that the provided close
 * functional will be called no more than one time.
 *
 * @param <T> type </T>
 */
internal class DefaultAutoCloseableIterator<T>(
    iterator: Iterator<T>,
    onClose: VoidCallable,
    airbyteStream: AirbyteStreamNameNamespacePair?
) : AbstractIterator<T>(), AutoCloseableIterator<T> {
    override val airbyteStream: Optional<AirbyteStreamNameNamespacePair>
    private val iterator: Iterator<T>
    private val onClose: VoidCallable

    private var hasClosed: Boolean

    init {
        Preconditions.checkNotNull(iterator)
        Preconditions.checkNotNull(onClose)

        this.airbyteStream = Optional.ofNullable(airbyteStream)
        this.iterator = iterator
        this.onClose = onClose
        this.hasClosed = false
    }

    override fun computeNext(): T? {
        assertHasNotClosed()

        return if (iterator.hasNext()) {
            iterator.next()
        } else {
            endOfData()
        }
    }

    @Throws(Exception::class)
    override fun close() {
        if (!hasClosed) {
            hasClosed = true
            onClose.call()
        }
    }

    private fun assertHasNotClosed() {
        Preconditions.checkState(!hasClosed)
    }
}
