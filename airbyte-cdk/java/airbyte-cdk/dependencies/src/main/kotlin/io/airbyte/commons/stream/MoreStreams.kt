/*
 * Copyright (c) 2023 Airbyte, Inc., all rights reserved.
 */
package io.airbyte.commons.stream

import java.util.*
import java.util.stream.Stream
import java.util.stream.StreamSupport

object MoreStreams {
    fun <T> toStream(iterator: Iterator<T>?): Stream<T> {
        return StreamSupport.stream(
            Spliterators.spliteratorUnknownSize(iterator, Spliterator.ORDERED),
            false
        )
    }

    fun <T> toStream(iterable: Iterable<T>): Stream<T> {
        return toStream(iterable.iterator())
    }
}
